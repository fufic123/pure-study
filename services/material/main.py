from app.api.routers.material_router import router as material_router
from app.logging_config import setup_logging
from fastapi import FastAPI

setup_logging()

app = FastAPI(title="Material Service")

app.include_router(material_router, prefix="/material", tags=["material"])


@app.get("/material/health")
async def health() -> dict:
    return {"status": "ok"}
