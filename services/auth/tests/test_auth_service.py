import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.auth_service import AuthService
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_register_creates_user_and_returns_tokens(mock_session, mock_user):
    with (
        patch("app.services.auth_service.UserRepository") as MockUserRepo,
        patch("app.services.auth_service.RefreshTokenRepository") as MockTokenRepo,
    ):
        MockUserRepo.return_value.get_by_email = AsyncMock(return_value=None)
        MockUserRepo.return_value.create = AsyncMock(return_value=mock_user)
        MockTokenRepo.return_value.create = AsyncMock()

        result = await AuthService(mock_session).register("new@example.com", "password123")

        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"
        MockUserRepo.return_value.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_duplicate_email_raises_409(mock_session, mock_user):
    with patch("app.services.auth_service.UserRepository") as MockUserRepo:
        MockUserRepo.return_value.get_by_email = AsyncMock(return_value=mock_user)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).register("test@example.com", "pass")

        assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_login_valid_credentials_returns_tokens(mock_session, mock_user):
    with (
        patch("app.services.auth_service.UserRepository") as MockUserRepo,
        patch("app.services.auth_service.RefreshTokenRepository") as MockTokenRepo,
        patch("app.services.auth_service._verify_password", return_value=True),
    ):
        MockUserRepo.return_value.get_by_email = AsyncMock(return_value=mock_user)
        MockTokenRepo.return_value.create = AsyncMock()

        result = await AuthService(mock_session).login("test@example.com", "password123")

        assert result.access_token
        assert result.refresh_token


@pytest.mark.asyncio
async def test_login_wrong_password_raises_401(mock_session, mock_user):
    with (
        patch("app.services.auth_service.UserRepository") as MockUserRepo,
        patch("app.services.auth_service._verify_password", return_value=False),
    ):
        MockUserRepo.return_value.get_by_email = AsyncMock(return_value=mock_user)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).login("test@example.com", "wrong")

        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_raises_401(mock_session):
    with patch("app.services.auth_service.UserRepository") as MockUserRepo:
        MockUserRepo.return_value.get_by_email = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).login("nobody@example.com", "pass")

        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_valid_token_rotates_and_returns_new_tokens(mock_session, mock_refresh_token):
    with (
        patch("app.services.auth_service.UserRepository"),
        patch("app.services.auth_service.RefreshTokenRepository") as MockTokenRepo,
    ):
        MockTokenRepo.return_value.get_by_hash = AsyncMock(return_value=mock_refresh_token)
        MockTokenRepo.return_value.revoke = AsyncMock()
        MockTokenRepo.return_value.create = AsyncMock()

        result = await AuthService(mock_session).refresh("some-raw-refresh-token")

        assert result.access_token
        MockTokenRepo.return_value.revoke.assert_called_once_with(mock_refresh_token.id)


@pytest.mark.asyncio
async def test_refresh_invalid_token_raises_401(mock_session):
    with patch("app.services.auth_service.RefreshTokenRepository") as MockTokenRepo:
        MockTokenRepo.return_value.get_by_hash = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await AuthService(mock_session).refresh("bad-token")

        assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_token(mock_session, mock_refresh_token):
    with patch("app.services.auth_service.RefreshTokenRepository") as MockTokenRepo:
        MockTokenRepo.return_value.get_by_hash = AsyncMock(return_value=mock_refresh_token)
        MockTokenRepo.return_value.revoke = AsyncMock()

        await AuthService(mock_session).logout("some-raw-token")

        MockTokenRepo.return_value.revoke.assert_called_once_with(mock_refresh_token.id)


@pytest.mark.asyncio
async def test_logout_nonexistent_token_is_noop(mock_session):
    with patch("app.services.auth_service.RefreshTokenRepository") as MockTokenRepo:
        MockTokenRepo.return_value.get_by_hash = AsyncMock(return_value=None)
        MockTokenRepo.return_value.revoke = AsyncMock()

        await AuthService(mock_session).logout("nonexistent-token")

        MockTokenRepo.return_value.revoke.assert_not_called()
