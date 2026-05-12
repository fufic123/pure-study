import logging

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.token_response import TokenResponse
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.token_service import TokenService

log = logging.getLogger("auth_service")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)
        self.token_svc = TokenService()

    async def register(self, email: str, password: str) -> TokenResponse:
        log.debug("register attempt | email=%s", email)
        if await self.user_repo.get_by_email(email):
            log.warning("register conflict | email=%s already exists", email)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed_password = _hash_password(password)
        user = await self.user_repo.create(email=email, hashed_password=hashed_password)
        log.info("registered | user_id=%s email=%s", user.id, email)
        return await self._issue_tokens(user.id)

    async def login(self, email: str, password: str) -> TokenResponse:
        log.debug("login attempt | email=%s", email)
        user = await self.user_repo.get_by_email(email)
        if not user or not user.hashed_password or not _verify_password(password, user.hashed_password):
            log.warning("login failed | email=%s | reason=%s",
                        email, "user not found" if not user else "wrong password")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        log.info("login ok | user_id=%s email=%s", user.id, email)
        return await self._issue_tokens(user.id)

    async def refresh(self, raw_token: str) -> TokenResponse:
        token_hash = self.token_svc.hash_refresh_token(raw_token)
        record = await self.token_repo.get_by_hash(token_hash)
        if not record:
            log.warning("refresh failed | token not found or revoked")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        await self.token_repo.revoke(record.id)
        log.info("token refreshed | user_id=%s", record.user_id)
        return await self._issue_tokens(record.user_id)

    async def logout(self, raw_token: str) -> None:
        token_hash = self.token_svc.hash_refresh_token(raw_token)
        record = await self.token_repo.get_by_hash(token_hash)
        if record:
            await self.token_repo.revoke(record.id)
            await self.session.commit()
            log.info("logout | user_id=%s", record.user_id)
        else:
            log.debug("logout called with unknown/already-revoked token")

    async def _issue_tokens(self, user_id) -> TokenResponse:
        access_token = self.token_svc.create_access_token(user_id)
        raw_refresh, refresh_hash = self.token_svc.generate_refresh_token()
        expires_at = self.token_svc.refresh_token_expires_at()

        await self.token_repo.create(user_id, refresh_hash, expires_at)
        await self.session.commit()

        log.debug("tokens issued | user_id=%s", user_id)
        return TokenResponse(access_token=access_token, refresh_token=raw_refresh)
