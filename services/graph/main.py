from contextlib import asynccontextmanager

from app.api.routers.graph_router import router as graph_router
from app.falkordb.session import close_client, init_client
from app.logging_config import setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from fastapi import FastAPI

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_client()
    yield
    await close_client()


app = FastAPI(title="Graph Service", lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(graph_router, prefix="/graph", tags=["graph"])


@app.get("/graph/health")
async def health() -> dict:
    return {"status": "ok"}
