from fastapi import FastAPI

app = FastAPI(title="AI Service")


@app.get("/ai/health")
async def health() -> dict:
    return {"status": "ok"}
