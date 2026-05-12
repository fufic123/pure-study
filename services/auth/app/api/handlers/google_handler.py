from fastapi import Depends, Query
from fastapi.responses import RedirectResponse
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

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
    tokens = await GoogleService(session).handle_callback(code)
    redirect_url = (
        f"{settings.frontend_url}/auth/callback"
        f"?access_token={tokens.access_token}"
        f"&refresh_token={tokens.refresh_token}"
    )
    return RedirectResponse(url=redirect_url, status_code=302)
