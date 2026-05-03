from fastapi import APIRouter

from app.api.handlers.auth_handler import (
    login_handler,
    logout_handler,
    refresh_handler,
    register_handler,
)

router = APIRouter()

router.post("/register", summary="Register with email + password")(register_handler)
router.post("/login", summary="Login with email + password")(login_handler)
router.post("/refresh", summary="Rotate refresh token")(refresh_handler)
router.post("/logout", summary="Revoke refresh token")(logout_handler)
