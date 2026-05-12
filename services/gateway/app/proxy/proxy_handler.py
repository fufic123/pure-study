import logging
import time

import httpx
from settings import settings
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger("proxy")

_HOP_BY_HOP = frozenset({"transfer-encoding", "connection", "keep-alive", "te", "trailers", "upgrade"})

_ROUTE_MAP: list[tuple[str, str]] = [
    ("/auth/", settings.auth_service_url),
    ("/graph/", settings.graph_service_url),
    ("/ai/", settings.ai_service_url),
    ("/material/", settings.material_service_url),
    ("/check/", settings.check_service_url),
]


class ProxyHandler:
    async def forward(self, request: Request) -> Response:
        path = request.url.path
        target_base = next(
            (base for prefix, base in _ROUTE_MAP if path.startswith(prefix)),
            None,
        )

        if target_base is None:
            log.warning("no route for path=%s", path)
            return Response(content=b'{"detail":"Not found"}', status_code=404, media_type="application/json")

        query = request.url.query
        url = f"{target_base}{path}" + (f"?{query}" if query else "")
        user_id = getattr(request.state, "user_id", None)

        log.debug(
            "%s %s → %s | user=%s",
            request.method, path, target_base, user_id or "anon",
        )

        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ("host", "authorization", "content-length")
        }
        if user_id:
            headers["x-user-id"] = str(user_id)
        rid = getattr(request.state, "request_id", None)
        if rid:
            headers["x-request-id"] = rid

        body = await request.body()
        http_client: httpx.AsyncClient = request.app.state.http_client

        t0 = time.monotonic()
        try:
            upstream = await http_client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
            )
        except Exception as exc:
            elapsed = int((time.monotonic() - t0) * 1000)
            log.error(
                "%s %s → upstream error after %dms: %s",
                request.method, path, elapsed, exc,
            )
            raise

        elapsed = int((time.monotonic() - t0) * 1000)
        level = logging.WARNING if upstream.status_code >= 400 else logging.INFO
        log.log(
            level,
            "%s %s | user=%s | %d | %dms | %d bytes",
            request.method, path, user_id or "anon",
            upstream.status_code, elapsed, len(upstream.content),
        )
        if upstream.status_code >= 500:
            log.error("upstream 5xx body: %s", upstream.text[:500])

        response_headers = {
            k: v for k, v in upstream.headers.items() if k.lower() not in _HOP_BY_HOP
        }
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=response_headers,
        )
