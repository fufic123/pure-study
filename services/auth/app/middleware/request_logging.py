import logging
import time
import uuid

from app.logging_config import request_id_var
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger("request")

_SKIP_PATHS = frozenset({"/health", "/docs", "/openapi.json", "/redoc"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)

        log.info("Processing Request  %s %s", request.method, request.url.path)
        t0 = time.monotonic()
        try:
            response = await call_next(request)
        except Exception:
            ms = int((time.monotonic() - t0) * 1000)
            log.error("Request failed      %s %s  %dms", request.method, request.url.path, ms)
            request_id_var.reset(token)
            raise

        ms = int((time.monotonic() - t0) * 1000)
        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        log.log(level, "Request processed   %s %s  %d  %dms",
                request.method, request.url.path, response.status_code, ms)

        response.headers["x-request-id"] = rid
        request_id_var.reset(token)
        return response
