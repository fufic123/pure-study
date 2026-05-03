from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from settings import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/auth/"):
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            return await call_next(request)

        redis = request.app.state.redis
        key = f"rate_limit:{user_id}"

        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, settings.rate_limit_window_seconds)

        if count > settings.rate_limit_requests:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

        return await call_next(request)
