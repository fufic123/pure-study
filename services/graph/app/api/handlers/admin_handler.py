"""Admin endpoints — return data across ALL user graphs.

These bypass the per-request x-user-id and instead enumerate every
named graph in FalkorDB. The gateway is responsible for restricting
access to admins (via JWT.is_admin); this handler trusts that gate.
"""

import asyncio
import logging
from typing import Any

from app.falkordb.session import AsyncGraph, get_client

log = logging.getLogger("graph_admin")


def _list_user_graphs() -> list[tuple[str, AsyncGraph]]:
    """Enumerate all `user:<uuid>` graphs known to FalkorDB."""
    raw = get_client().connection.execute_command("GRAPH.LIST")
    names = [n.decode() if isinstance(n, bytes) else n for n in raw or []]
    out: list[tuple[str, AsyncGraph]] = []
    client = get_client()
    for name in names:
        if name.startswith("user:"):
            user_id = name[len("user:"):]
            out.append((user_id, AsyncGraph(client.select_graph(name), name)))
    return out


class AdminGraphHandler:
    async def list_all_courses(self) -> list[dict[str, Any]]:
        graphs = await asyncio.to_thread(_list_user_graphs)
        out: list[dict[str, Any]] = []
        for user_id, g in graphs:
            try:
                result = await g.query("MATCH (c:Course) RETURN c")
                for row in result.result_set:
                    props = dict(row[0].properties)
                    props["user_id"] = user_id
                    out.append(props)
            except Exception as exc:
                log.warning("courses query failed for %s: %s", user_id, exc)
        log.info("admin list_all_courses | users=%d total=%d", len(graphs), len(out))
        return out

    async def list_all_topics(self) -> list[dict[str, Any]]:
        graphs = await asyncio.to_thread(_list_user_graphs)
        out: list[dict[str, Any]] = []
        for user_id, g in graphs:
            try:
                result = await g.query(
                    """
                    MATCH (t:Topic)
                    OPTIONAL MATCH (c:Course)-[:CONTAINS]->(t)
                    OPTIONAL MATCH (t)-[:REQUIRES]->(req:Topic)
                    RETURN t, c.id AS course_id, c.name AS course_name, collect(req.id) AS prereqs
                    """
                )
                for row in result.result_set:
                    props = dict(row[0].properties)
                    props["course_id"] = row[1]
                    props["course_name"] = row[2]
                    props["prereqs"] = [p for p in (row[3] or []) if p]
                    props["user_id"] = user_id
                    out.append(props)
            except Exception as exc:
                log.warning("topics query failed for %s: %s", user_id, exc)
        log.info("admin list_all_topics | users=%d total=%d", len(graphs), len(out))
        return out

    async def list_all_edges(self) -> list[dict[str, Any]]:
        graphs = await asyncio.to_thread(_list_user_graphs)
        out: list[dict[str, Any]] = []
        for user_id, g in graphs:
            try:
                result = await g.query(
                    """
                    MATCH (a)-[r]->(b)
                    RETURN a.id AS from_id, type(r) AS edge_type, b.id AS to_id, a.name AS from_name, b.name AS to_name
                    """
                )
                for row in result.result_set:
                    out.append({
                        "user_id": user_id,
                        "from_id": row[0],
                        "edge_type": row[1],
                        "to_id": row[2],
                        "from_name": row[3],
                        "to_name": row[4],
                    })
            except Exception as exc:
                log.warning("edges query failed for %s: %s", user_id, exc)
        log.info("admin list_all_edges | users=%d total=%d", len(graphs), len(out))
        return out
