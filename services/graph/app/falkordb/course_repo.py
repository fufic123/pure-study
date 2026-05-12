import uuid


class CourseRepository:
    def __init__(self, graph) -> None:
        self.graph = graph

    async def create(self, name: str, goal: str, domain: str) -> dict:
        course_id = str(uuid.uuid4())
        await self.graph.query(
            "CREATE (:Course {id: $id, name: $name, goal: $goal, domain: $domain})",
            {"id": course_id, "name": name, "goal": goal, "domain": domain},
        )
        return {"id": course_id, "name": name, "goal": goal, "domain": domain}

    async def get(self, course_id: str) -> dict | None:
        result = await self.graph.query(
            "MATCH (c:Course {id: $id}) RETURN c",
            {"id": course_id},
        )
        if not result.result_set:
            return None
        return dict(result.result_set[0][0].properties)

    async def list_all(self) -> list[dict]:
        result = await self.graph.query("MATCH (c:Course) RETURN c")
        return [dict(row[0].properties) for row in result.result_set]
