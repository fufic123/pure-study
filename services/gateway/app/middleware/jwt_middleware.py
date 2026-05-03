import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from settings import settings


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/auth/"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing or invalid authorization header"}, status_code=401)

        token = auth_header.removeprefix("Bearer ")
        try:
            payload = jwt.decode(token, settings.public_key, algorithms=["RS256"])
            request.state.user_id = payload["sub"]
        except jwt.ExpiredSignatureError:
            return JSONResponse({"detail": "Token expired"}, status_code=401)
        except jwt.InvalidTokenError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        return await call_next(request)
