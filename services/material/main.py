from fastapi import FastAPI

app = FastAPI(title="Material Service")


@app.get("/material/health")
async def health() -> dict:
    return {"status": "ok"}
