import asyncio
import logging

from falkordb import FalkorDB
from settings import settings

log = logging.getLogger("falkordb")

_client: FalkorDB | None = None


class AsyncGraph:
    """Thin async wrapper around the synchronous falkordb.Graph.
    Runs each query in a thread so the event loop is never blocked.
    """

    def __init__(self, graph, graph_name: str = "") -> None:
        self._graph = graph
        self._name = graph_name

    async def query(self, q: str, params: dict | None = None):
        q_preview = q.strip().replace("\n", " ")[:120]
        log.debug("QUERY [%s] %s | params=%s", self._name, q_preview, params)
        if params:
            return await asyncio.to_thread(self._graph.query, q, params)
        return await asyncio.to_thread(self._graph.query, q)


async def init_client() -> None:
    global _client
    log.info("connecting to FalkorDB at %s:%s", settings.falkordb_host, settings.falkordb_port)
    _client = await asyncio.to_thread(
        FalkorDB, settings.falkordb_host, settings.falkordb_port
    )
    log.info("FalkorDB connected")


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.connection.close()
        _client = None
        log.info("FalkorDB connection closed")


def get_client() -> FalkorDB:
    if _client is None:
        raise RuntimeError("FalkorDB client is not initialised")
    return _client


def get_user_graph(user_id: str) -> AsyncGraph:
    graph_name = f"user:{user_id}"
    log.debug("selecting graph %s", graph_name)
    return AsyncGraph(get_client().select_graph(graph_name), graph_name)
