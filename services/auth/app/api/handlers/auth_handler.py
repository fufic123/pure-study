from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.login_request import LoginRequest
from app.api.dtos.logout_request import LogoutRequest
from app.api.dtos.refresh_request import RefreshRequest
from app.api.dtos.register_request import RegisterRequest
from app.api.dtos.token_response import TokenResponse
from app.db.session import get_session
from app.services.auth_service import AuthService


async def register_handler(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    return await AuthService(session).register(body.email, body.password)


async def login_handler(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    return await AuthService(session).login(body.email, body.password)


async def refresh_handler(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    return await AuthService(session).refresh(body.refresh_token)


async def logout_handler(
    body: LogoutRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    await AuthService(session).logout(body.refresh_token)
    return {"detail": "Logged out"}
