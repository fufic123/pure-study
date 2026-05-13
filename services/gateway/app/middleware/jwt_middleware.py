import logging

import jwt
from settings import settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

log = logging.getLogger("jwt")


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/auth/"):
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
