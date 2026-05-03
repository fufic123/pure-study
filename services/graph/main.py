from fastapi import FastAPI

app = FastAPI(title="Graph Service")


@app.get("/graph/health")
async def health() -> dict:
    return {"status": "ok"}
