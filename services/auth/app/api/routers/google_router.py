from fastapi import APIRouter

from app.api.handlers.google_handler import (
    google_auth_url_handler,
    google_callback_handler,
)

router = APIRouter()

router.get("", summary="Get Google OAuth authorization URL")(google_auth_url_handler)
router.get("/callback", summary="Google OAuth callback")(google_callback_handler)
