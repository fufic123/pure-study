import logging

import jwt
from settings import settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

log = logging.getLogger("jwt")

# Paths that don't require an access token. Everything else under /auth/
# (notably /auth/users/*, /auth/me) goes through the same JWT check as the
# rest of the gateway.
_PUBLIC_PATHS = (
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/auth/logout",
    "/auth/google",
    "/auth/google/callback",
)


def _is_public(path: str) -> bool:
    if path in _PUBLIC_PATHS:
        return True
    # Allow nested google routes (e.g. /auth/google/anything) as part of the OAuth flow
    return path.startswith("/auth/google/")


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if _is_public(request.url.path):
            return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.removeprefix("Bearer ")

        if not token:
            log.warning("missing token | path=%s", request.url.path)
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        try:
            payload = jwt.decode(token, settings.public_key, algorithms=["RS256"])
            request.state.user_id = payload["sub"]
            log.debug("JWT ok | user=%s | path=%s", payload["sub"], request.url.path)
        except jwt.ExpiredSignatureError:
            log.warning("JWT expired | path=%s", request.url.path)
            return JSONResponse({"detail": "Token expired"}, status_code=401)
        except jwt.InvalidTokenError as exc:
            log.warning("JWT invalid | path=%s | %s", request.url.path, exc)
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        return await call_next(request)
