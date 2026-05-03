from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from app.proxy.proxy_handler import ProxyHandler

router = APIRouter()
_handler = ProxyHandler()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
async def proxy_route(request: Request, path: str) -> Response:
    return await _handler.forward(request)
