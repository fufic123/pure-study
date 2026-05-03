"""
HTTP integration tests — thin FastAPI app wired with real routers
but session and service methods mocked out.
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.api.dtos.token_response import TokenResponse
from app.api.routers.auth_router import router as auth_router
from app.api.routers.google_router import router as google_router
from app.db.session import get_session
from app.services.auth_service import AuthService
from app.services.google_service import GoogleService


@pytest.fixture
def test_app(mock_session) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_session] = lambda: mock_session
    app.include_router(auth_router, prefix="/auth")
    app.include_router(google_router, prefix="/auth/google")
    return app


@pytest.fixture
async def client(test_app) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as c:
        yield c


# ── register ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_returns_200_with_tokens(client, token_response):
    with patch.object(AuthService, "register", new=AsyncMock(return_value=token_response)):
        resp = await client.post("/auth/register", json={"email": "a@b.com", "password": "pass"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] == token_response.access_token
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_returns_409(client):
    with patch.object(AuthService, "register", new=AsyncMock(side_effect=HTTPException(409, "conflict"))):
        resp = await client.post("/auth/register", json={"email": "a@b.com", "password": "pass"})

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client):
    resp = await client.post("/auth/register", json={"email": "not-an-email", "password": "pass"})
    assert resp.status_code == 422


# ── login ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_returns_200_with_tokens(client, token_response):
    with patch.object(AuthService, "login", new=AsyncMock(return_value=token_response)):
        resp = await client.post("/auth/login", json={"email": "a@b.com", "password": "pass"})

    assert resp.status_code == 200
    assert resp.json()["refresh_token"] == token_response.refresh_token


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client):
    with patch.object(AuthService, "login", new=AsyncMock(side_effect=HTTPException(401, "invalid"))):
        resp = await client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})

    assert resp.status_code == 401


# ── refresh ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_returns_new_tokens(client, token_response):
    new_response = TokenResponse(access_token="new-access", refresh_token="new-refresh")
    with patch.object(AuthService, "refresh", new=AsyncMock(return_value=new_response)):
        resp = await client.post("/auth/refresh", json={"refresh_token": "old-token"})

    assert resp.status_code == 200
    assert resp.json()["access_token"] == "new-access"


# ── logout ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_logout_returns_200(client):
    with patch.object(AuthService, "logout", new=AsyncMock(return_value=None)):
        resp = await client.post("/auth/logout", json={"refresh_token": "some-token"})

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Logged out"


# ── google ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_google_auth_url_returns_url(client):
    with patch.object(GoogleService, "get_authorization_url", return_value="https://accounts.google.com/..."):
        resp = await client.get("/auth/google")

    assert resp.status_code == 200
    assert "url" in resp.json()


@pytest.mark.asyncio
async def test_google_callback_returns_tokens(client, token_response):
    with patch.object(GoogleService, "handle_callback", new=AsyncMock(return_value=token_response)):
        resp = await client.get("/auth/google/callback?code=test-auth-code")

    assert resp.status_code == 200
    assert resp.json()["access_token"] == token_response.access_token


@pytest.mark.asyncio
async def test_google_callback_missing_code_returns_422(client):
    resp = await client.get("/auth/google/callback")
    assert resp.status_code == 422
