import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.middleware.jwt_middleware import JWTMiddleware


def make_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(JWTMiddleware)

    @app.get("/auth/login")
    async def auth_route():
        return {"path": "auth"}

    @app.get("/graph/data")
    async def protected_route(request: Request):
        return {"user_id": getattr(request.state, "user_id", None)}

    return app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=make_test_app()), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_auth_routes_bypass_jwt_check(client):
    resp = await client.get("/auth/login")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_missing_auth_header_returns_401(client):
    resp = await client.get("/graph/data")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_non_bearer_scheme_returns_401(client):
    resp = await client.get("/graph/data", headers={"Authorization": "Basic dXNlcjpwYXNz"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_returns_401(client):
    resp = await client.get("/graph/data", headers={"Authorization": "Bearer garbage.token.here"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_returns_401(client, expired_token):
    resp = await client.get("/graph/data", headers={"Authorization": f"Bearer {expired_token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Token expired"


@pytest.mark.asyncio
async def test_valid_token_passes_and_sets_user_id(client, valid_token, sample_user_id):
    resp = await client.get("/graph/data", headers={"Authorization": f"Bearer {valid_token}"})
    assert resp.status_code == 200
    assert resp.json()["user_id"] == sample_user_id
