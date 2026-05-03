from fastapi import FastAPI

app = FastAPI(title="Check Service")


@app.get("/check/health")
async def health() -> dict:
    return {"status": "ok"}
