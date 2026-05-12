from typing import Literal

EdgeType = Literal["CONTAINS", "SUBTOPIC_OF", "REQUIRES", "RELATED_TO", "EQUIVALENT_TO"]

_VALID_EDGE_TYPES: frozenset[str] = frozenset(
    {"CONTAINS", "SUBTOPIC_OF", "REQUIRES", "RELATED_TO", "EQUIVALENT_TO"}
)


class EdgeRepository:
    def __init__(self, graph) -> None:
        self.graph = graph

    async def create(self, from_id: str, to_id: str, edge_type: str) -> None:
        if edge_type not in _VALID_EDGE_TYPES:
            raise ValueError(f"Invalid edge type '{edge_type}'")
        # Relationship type cannot be parameterised in Cypher — safe after allowlist check
        await self.graph.query(
            f"MATCH (a {{id: $from_id}}), (b {{id: $to_id}}) CREATE (a)-[:{edge_type}]->(b)",
            {"from_id": from_id, "to_id": to_id},
        )

    async def delete(self, from_id: str, to_id: str, edge_type: str) -> None:
        if edge_type not in _VALID_EDGE_TYPES:
            raise ValueError(f"Invalid edge type '{edge_type}'")
        await self.graph.query(
            f"MATCH (a {{id: $from_id}})-[r:{edge_type}]->(b {{id: $to_id}}) DELETE r",
            {"from_id": from_id, "to_id": to_id},
        )
