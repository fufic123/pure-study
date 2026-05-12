import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.proxy.proxy_handler import _ROUTE_MAP, ProxyHandler
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def _upstream_response(status_code: int = 200, body: bytes = b'{"ok":true}') -> MagicMock:
    resp = MagicMock()
    resp.content = body
    resp.status_code = status_code
    resp.headers = {"content-type": "application/json"}
    return resp


class _SetUserIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, user_id: str):
        super().__init__(app)
        self.user_id = user_id

    async def dispatch(self, request: Request, call_next):
        request.state.user_id = self.user_id
        return await call_next(request)


def make_test_app(mock_http_client, user_id: str | None = None) -> FastAPI:
    app = FastAPI()
    app.state.http_client = mock_http_client

    handler = ProxyHandler()

    if user_id:
        app.add_middleware(_SetUserIdMiddleware, user_id=user_id)

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def proxy(request: Request, path: str):
        return await handler.forward(request)

    return app


@pytest.fixture
def mock_http() -> AsyncMock:
    client = AsyncMock()
    client.request = AsyncMock(return_value=_upstream_response())
    return client


@pytest.fixture
async def client(mock_http) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=make_test_app(mock_http)), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_unknown_path_returns_404(client):
    resp = await client.get("/unknown/route")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_route_map_covers_all_prefixes():
    prefixes = {prefix for prefix, _ in _ROUTE_MAP}
    assert "/auth/" in prefixes
    assert "/graph/" in prefixes
    assert "/ai/" in prefixes
    assert "/material/" in prefixes
    assert "/check/" in prefixes


@pytest.mark.asyncio
async def test_auth_prefix_routed_to_auth_service(client, mock_http):
    await client.get("/auth/login")

    mock_http.request.assert_called_once()
    url = mock_http.request.call_args.kwargs["url"]
    assert "auth" in url and "/auth/login" in url


@pytest.mark.asyncio
async def test_authorization_header_stripped(client, mock_http):
    await client.get("/auth/me", headers={"Authorization": "Bearer some-token"})

    forwarded_headers = mock_http.request.call_args.kwargs["headers"]
    assert "authorization" not in {k.lower() for k in forwarded_headers}


@pytest.mark.asyncio
async def test_x_user_id_header_forwarded_when_user_id_set(mock_http):
    user_id = str(uuid.uuid4())
    app = make_test_app(mock_http, user_id=user_id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        await c.get("/graph/nodes")

    forwarded_headers = mock_http.request.call_args.kwargs["headers"]
    assert forwarded_headers.get("x-user-id") == user_id


@pytest.mark.asyncio
async def test_upstream_status_code_preserved(client, mock_http):
    mock_http.request.return_value = _upstream_response(status_code=201)

    resp = await client.post("/auth/register", json={})

    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_query_string_forwarded(client, mock_http):
    await client.get("/graph/search?q=python&limit=10")

    url = mock_http.request.call_args.kwargs["url"]
    assert "q=python" in url
    assert "limit=10" in url
