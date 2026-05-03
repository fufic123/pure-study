import httpx
from starlette.requests import Request
from starlette.responses import Response

from settings import settings

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
            return Response(content=b'{"detail":"Not found"}', status_code=404, media_type="application/json")

        query = request.url.query
        url = f"{target_base}{path}" + (f"?{query}" if query else "")

        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ("host", "authorization", "content-length")
        }
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            headers["x-user-id"] = str(user_id)

        body = await request.body()
        http_client: httpx.AsyncClient = request.app.state.http_client

        upstream = await http_client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
        )

        response_headers = {
            k: v for k, v in upstream.headers.items() if k.lower() not in _HOP_BY_HOP
        }
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=response_headers,
        )
