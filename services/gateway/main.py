from contextlib import asynccontextmanager

import httpx
import redis.asyncio as redis
from fastapi import FastAPI

from app.middleware.jwt_middleware import JWTMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.routers.proxy_router import router as proxy_router
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)
    yield
    await app.state.http_client.aclose()
    await app.state.redis.aclose()


app = FastAPI(title="Gateway", lifespan=lifespan)

# JWT runs first (outermost), then rate limit
app.add_middleware(RateLimitMiddleware)
app.add_middleware(JWTMiddleware)

app.include_router(proxy_router)
