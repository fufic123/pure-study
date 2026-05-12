import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.google_service import GoogleService

_GOOGLE_USER_INFO = {"id": "google-uid-123", "email": "user@gmail.com"}


@pytest.fixture
def svc(mock_session) -> GoogleService:
    return GoogleService(mock_session)


def test_get_authorization_url_contains_required_params(svc):
    url = svc.get_authorization_url()

    assert "accounts.google.com" in url
    assert "client_id=test-google-client-id" in url
    assert "response_type=code" in url
    assert "scope=" in url


@pytest.mark.asyncio
async def test_callback_existing_google_user_logs_in(mock_session, mock_user):
    with (
        patch("app.services.google_service.UserRepository") as MockUserRepo,
        patch("app.services.google_service.RefreshTokenRepository") as MockTokenRepo,
        patch.object(GoogleService, "_exchange_code", new=AsyncMock(return_value="g-access-token")),
        patch.object(GoogleService, "_fetch_user_info", new=AsyncMock(return_value=_GOOGLE_USER_INFO)),
    ):
        MockUserRepo.return_value.get_by_google_id = AsyncMock(return_value=mock_user)
        MockUserRepo.return_value.create = AsyncMock()
        MockUserRepo.return_value.update_google_id = AsyncMock()
        MockTokenRepo.return_value.create = AsyncMock()

        result = await GoogleService(mock_session).handle_callback("auth-code")

        assert result.access_token
        MockUserRepo.return_value.create.assert_not_called()
        MockUserRepo.return_value.update_google_id.assert_not_called()


@pytest.mark.asyncio
async def test_callback_existing_email_links_google_id(mock_session, mock_user):
    with (
        patch("app.services.google_service.UserRepository") as MockUserRepo,
        patch("app.services.google_service.RefreshTokenRepository") as MockTokenRepo,
        patch.object(GoogleService, "_exchange_code", new=AsyncMock(return_value="g-access-token")),
        patch.object(GoogleService, "_fetch_user_info", new=AsyncMock(return_value=_GOOGLE_USER_INFO)),
    ):
        MockUserRepo.return_value.get_by_google_id = AsyncMock(return_value=None)
        MockUserRepo.return_value.get_by_email = AsyncMock(return_value=mock_user)
        MockUserRepo.return_value.update_google_id = AsyncMock(return_value=mock_user)
        MockTokenRepo.return_value.create = AsyncMock()

        await GoogleService(mock_session).handle_callback("auth-code")

        MockUserRepo.return_value.update_google_id.assert_called_once_with(
            mock_user.id, _GOOGLE_USER_INFO["id"]
        )
        MockUserRepo.return_value.create.assert_not_called()


@pytest.mark.asyncio
async def test_callback_new_user_creates_account(mock_session, mock_user):
    with (
        patch("app.services.google_service.UserRepository") as MockUserRepo,
        patch("app.services.google_service.RefreshTokenRepository") as MockTokenRepo,
        patch.object(GoogleService, "_exchange_code", new=AsyncMock(return_value="g-access-token")),
        patch.object(GoogleService, "_fetch_user_info", new=AsyncMock(return_value=_GOOGLE_USER_INFO)),
    ):
        MockUserRepo.return_value.get_by_google_id = AsyncMock(return_value=None)
        MockUserRepo.return_value.get_by_email = AsyncMock(return_value=None)
        MockUserRepo.return_value.create = AsyncMock(return_value=mock_user)
        MockTokenRepo.return_value.create = AsyncMock()

        await GoogleService(mock_session).handle_callback("auth-code")

        MockUserRepo.return_value.create.assert_called_once_with(
            email=_GOOGLE_USER_INFO["email"],
            google_id=_GOOGLE_USER_INFO["id"],
        )
