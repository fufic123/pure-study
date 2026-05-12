import httpx
from settings import settings


class GraphClient:
    """HTTP client for the graph service. Passes user_id as x-user-id header."""

    def __init__(self, user_id: str) -> None:
        self._headers = {"x-user-id": user_id}

    async def create_course(self, name: str, goal: str, domain: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.graph_service_url}/graph/courses",
                json={"name": name, "goal": goal, "domain": domain},
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def create_topic(self, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.graph_service_url}/graph/topics",
                json=payload,
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def create_edge(self, from_id: str, to_id: str, edge_type: str) -> None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.graph_service_url}/graph/edges",
                json={"from_id": from_id, "to_id": to_id, "edge_type": edge_type},
                headers=self._headers,
            )
            resp.raise_for_status()

    async def mark_content_ready(self, topic_id: str) -> None:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.graph_service_url}/graph/topics/{topic_id}/content-ready",
                headers=self._headers,
            )
            resp.raise_for_status()

    async def get_topic(self, topic_id: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{settings.graph_service_url}/graph/topics/{topic_id}",
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_available_topics(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{settings.graph_service_url}/graph/topics/available",
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()
