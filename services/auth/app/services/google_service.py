import httpx
from fastapi import HTTPException, status
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.token_response import TokenResponse
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.token_service import TokenService

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class GoogleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)
        self.token_svc = TokenService()

    def get_authorization_url(self) -> str:
        params = "&".join([
            f"client_id={settings.google_client_id}",
            f"redirect_uri={settings.google_redirect_uri}",
            "response_type=code",
            "scope=openid%20email%20profile",
            "access_type=offline",
        ])
        return f"{_GOOGLE_AUTH_URL}?{params}"

    async def handle_callback(self, code: str) -> TokenResponse:
        google_access_token = await self._exchange_code(code)
        user_info = await self._fetch_user_info(google_access_token)

        google_id: str = user_info["id"]
        email: str = user_info["email"]

        user = await self.user_repo.get_by_google_id(google_id)

        if not user:
            user = await self.user_repo.get_by_email(email)
            if user:
                await self.user_repo.update_google_id(user.id, google_id)
            else:
                user = await self.user_repo.create(email=email, google_id=google_id)

        return await self._issue_tokens(user.id)

    async def _exchange_code(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                    "code": code,
                },
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google token exchange failed")
        return resp.json()["access_token"]

    async def _fetch_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                _GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google userinfo fetch failed")
        return resp.json()

    async def _issue_tokens(self, user_id) -> TokenResponse:
        access_token = self.token_svc.create_access_token(user_id)
        raw_refresh, refresh_hash = self.token_svc.generate_refresh_token()
        expires_at = self.token_svc.refresh_token_expires_at()

        await self.token_repo.create(user_id, refresh_hash, expires_at)
        await self.session.commit()

        return TokenResponse(access_token=access_token, refresh_token=raw_refresh)
