from fastapi import Depends, Query
from fastapi.responses import RedirectResponse
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.token_response import TokenResponse
from app.api.handlers.auth_handler import _ACCESS_MAX_AGE, _REFRESH_MAX_AGE
from app.db.session import get_session
from app.services.google_service import GoogleService


async def google_auth_url_handler(
    session: AsyncSession = Depends(get_session),
) -> dict:
    return {"url": GoogleService(session).get_authorization_url()}


async def google_callback_handler(
    code: str = Query(..., description="Authorization code from Google"),
    state: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    tokens, _email, _is_admin = await GoogleService(session).handle_callback(code)
    response = RedirectResponse(url=f"{settings.frontend_url}/auth/callback", status_code=302)
    response.set_cookie(
        "access_token", tokens.access_token,
        httponly=True, samesite="lax", max_age=_ACCESS_MAX_AGE, path="/",
    )
    response.set_cookie(
        "refresh_token", tokens.refresh_token,
        httponly=True, samesite="lax", max_age=_REFRESH_MAX_AGE, path="/",
    )
    return response
