from contextlib import asynccontextmanager

from app.api.routers.auth_router import router as auth_router
from app.api.routers.google_router import router as google_router
from app.db.session import Base, engine
from app.logging_config import setup_logging
from fastapi import FastAPI

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Auth Service", lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(google_router, prefix="/auth/google", tags=["google"])
