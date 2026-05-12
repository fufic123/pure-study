import pytest
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class _InjectUserIdMiddleware(BaseHTTPMiddleware):
    """Simulates what JWTMiddleware does: sets user_id on state."""

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/auth/"):
            request.state.user_id = "test-user-id"
        return await call_next(request)


def make_test_app(mock_redis) -> FastAPI:
    app = FastAPI()
    # Outermost = added last: inject user_id first, then rate-limit
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(_InjectUserIdMiddleware)
    app.state.redis = mock_redis

    @app.get("/auth/login")
    async def auth_route():
        return {"ok": True}

    @app.get("/graph/data")
    async def protected_route():
        return {"ok": True}

    return app


@pytest.fixture
async def client(mock_redis) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=make_test_app(mock_redis)), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_auth_routes_are_not_rate_limited(client, mock_redis):
    resp = await client.get("/auth/login")
    assert resp.status_code == 200
    mock_redis.incr.assert_not_called()


@pytest.mark.asyncio
async def test_first_request_sets_expiry_window(client, mock_redis):
    mock_redis.incr.return_value = 1

    resp = await client.get("/graph/data")

    assert resp.status_code == 200
    mock_redis.incr.assert_called_once_with("rate_limit:test-user-id")
    mock_redis.expire.assert_called_once()


@pytest.mark.asyncio
async def test_subsequent_requests_skip_expiry(client, mock_redis):
    mock_redis.incr.return_value = 5  # Not the first hit

    await client.get("/graph/data")

    mock_redis.expire.assert_not_called()


@pytest.mark.asyncio
async def test_request_at_limit_passes(client, mock_redis):
    mock_redis.incr.return_value = 100

    resp = await client.get("/graph/data")

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_request_over_limit_returns_429(client, mock_redis):
    mock_redis.incr.return_value = 101

    resp = await client.get("/graph/data")

    assert resp.status_code == 429
    assert resp.json()["detail"] == "Rate limit exceeded"
