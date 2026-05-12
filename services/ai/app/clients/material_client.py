import httpx
from settings import settings


class MaterialClient:
    """HTTP client for the material service."""

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.material_service_url}/material/search",
                json={"query": query, "limit": limit},
            )
            resp.raise_for_status()
            return resp.json()

    async def fetch_topics(self, source_id: str, course_id: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{settings.material_service_url}/material/sources/{source_id}/courses/{course_id}/topics",
            )
            resp.raise_for_status()
            return resp.json()
