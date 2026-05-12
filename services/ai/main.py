from app.api.routers.ai_router import router as ai_router
from app.logging_config import setup_logging
from fastapi import FastAPI

setup_logging()

app = FastAPI(title="AI Service")

app.include_router(ai_router, prefix="/ai", tags=["ai"])


@app.get("/ai/health")
async def health() -> dict:
    return {"status": "ok"}
