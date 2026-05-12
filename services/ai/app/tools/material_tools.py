"""Async tool handlers that call the material service."""

from app.clients.material_client import MaterialClient


def make_material_tools():
    material = MaterialClient()

    async def search_materials(inp: dict) -> list:
        return await material.search(inp["query"], limit=inp.get("limit", 5))

    async def fetch_course_topics(inp: dict) -> dict:
        return await material.fetch_topics(inp["source_id"], inp["course_id"])

    return {
        "search_materials": search_materials,
        "fetch_course_topics": fetch_course_topics,
    }
