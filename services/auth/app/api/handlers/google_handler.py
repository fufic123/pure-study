from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dtos.token_response import TokenResponse
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
) -> TokenResponse:
    return await GoogleService(session).handle_callback(code)
