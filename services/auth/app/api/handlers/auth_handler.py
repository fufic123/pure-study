from fastapi import Cookie, Depends, HTTPException, Response, status
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.login_request import LoginRequest
from app.api.dtos.register_request import RegisterRequest
from app.api.dtos.token_response import TokenResponse
from app.db.session import get_session
from app.services.auth_service import AuthService

_ACCESS_MAX_AGE = settings.access_token_expire_minutes * 60
_REFRESH_MAX_AGE = settings.refresh_token_expire_days * 24 * 60 * 60


def _set_token_cookies(response: Response, tokens: TokenResponse) -> None:
    response.set_cookie(
        "access_token", tokens.access_token,
        httponly=True, samesite="lax", max_age=_ACCESS_MAX_AGE, path="/",
    )
    response.set_cookie(
        "refresh_token", tokens.refresh_token,
        httponly=True, samesite="lax", max_age=_REFRESH_MAX_AGE, path="/",
    )


def _clear_token_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


async def register_handler(
    body: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    tokens, email, is_admin = await AuthService(session).register(body.email, body.password)
    _set_token_cookies(response, tokens)
    return {"email": email, "is_admin": is_admin}


async def login_handler(
    body: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict:
    tokens, email, is_admin = await AuthService(session).login(body.email, body.password)
    _set_token_cookies(response, tokens)
    return {"email": email, "is_admin": is_admin}


async def refresh_handler(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    tokens, email, is_admin = await AuthService(session).refresh(refresh_token)
    _set_token_cookies(response, tokens)
    return {"email": email, "is_admin": is_admin}


async def logout_handler(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
) -> dict:
    if refresh_token:
        await AuthService(session).logout(refresh_token)
    _clear_token_cookies(response)
    return {"detail": "Logged out"}
