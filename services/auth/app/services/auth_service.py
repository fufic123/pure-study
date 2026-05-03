from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.token_response import TokenResponse
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.token_service import TokenService

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)
        self.token_svc = TokenService()

    async def register(self, email: str, password: str) -> TokenResponse:
        if await self.user_repo.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed_password = _pwd_context.hash(password)
        user = await self.user_repo.create(email=email, hashed_password=hashed_password)
        return await self._issue_tokens(user.id)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.hashed_password or not _pwd_context.verify(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        return await self._issue_tokens(user.id)

    async def refresh(self, raw_token: str) -> TokenResponse:
        token_hash = self.token_svc.hash_refresh_token(raw_token)
        record = await self.token_repo.get_by_hash(token_hash)
        if not record:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        await self.token_repo.revoke(record.id)
        return await self._issue_tokens(record.user_id)

    async def logout(self, raw_token: str) -> None:
        token_hash = self.token_svc.hash_refresh_token(raw_token)
        record = await self.token_repo.get_by_hash(token_hash)
        if record:
            await self.token_repo.revoke(record.id)
            await self.session.commit()

    async def _issue_tokens(self, user_id) -> TokenResponse:
        access_token = self.token_svc.create_access_token(user_id)
        raw_refresh, refresh_hash = self.token_svc.generate_refresh_token()
        expires_at = self.token_svc.refresh_token_expires_at()

        await self.token_repo.create(user_id, refresh_hash, expires_at)
        await self.session.commit()

        return TokenResponse(access_token=access_token, refresh_token=raw_refresh)
