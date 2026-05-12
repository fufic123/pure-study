"""Async tool handlers that call the graph service. Each returns a plain dict."""

from app.clients.graph_client import GraphClient


def make_graph_tools(user_id: str):
    graph = GraphClient(user_id)

    async def create_course(inp: dict) -> dict:
        return await graph.create_course(inp["name"], inp["goal"], inp["domain"])

    async def create_topic(inp: dict) -> dict:
        return await graph.create_topic(inp)

    async def create_edge(inp: dict) -> dict:
        await graph.create_edge(inp["from_id"], inp["to_id"], inp["edge_type"])
        return {"ok": True}

    async def get_topic(inp: dict) -> dict:
        return await graph.get_topic(inp["topic_id"])

    async def get_available_topics(_inp: dict) -> list:
        return await graph.get_available_topics()

    return {
        "create_course": create_course,
        "create_topic": create_topic,
        "create_edge": create_edge,
        "get_topic": get_topic,
        "get_available_topics": get_available_topics,
    }
