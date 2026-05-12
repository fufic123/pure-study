import uuid

from app.domain.topic import TopicStatus


class TopicRepository:
    def __init__(self, graph) -> None:
        self.graph = graph

    async def create(
        self,
        name: str,
        slug: str,
        domain: str,
        description: str,
        complexity: int,
        status: TopicStatus = TopicStatus.LOCKED,
    ) -> dict:
        topic_id = str(uuid.uuid4())
        props = {
            "id": topic_id,
            "name": name,
            "slug": slug,
            "domain": domain,
            "description": description,
            "complexity": complexity,
            "status": status.value,
            "explanation_level": 1,
            "content_ready": False,
        }
        await self.graph.query(
            """CREATE (:Topic {
                id: $id, name: $name, slug: $slug, domain: $domain,
                description: $description, complexity: $complexity,
                status: $status, explanation_level: $explanation_level,
                content_ready: $content_ready
            })""",
            props,
        )
        return props

    async def get(self, topic_id: str) -> dict | None:
        result = await self.graph.query(
            "MATCH (t:Topic {id: $id}) RETURN t",
            {"id": topic_id},
        )
        if not result.result_set:
            return None
        return dict(result.result_set[0][0].properties)

    async def list_by_course(self, course_id: str) -> list[dict]:
        result = await self.graph.query(
            "MATCH (c:Course {id: $id})-[:CONTAINS]->(t:Topic) RETURN t",
            {"id": course_id},
        )
        return [dict(row[0].properties) for row in result.result_set]

    async def list_by_status(self, status: TopicStatus) -> list[dict]:
        result = await self.graph.query(
            "MATCH (t:Topic {status: $status}) RETURN t",
            {"status": status.value},
        )
        return [dict(row[0].properties) for row in result.result_set]

    async def update_status(self, topic_id: str, status: TopicStatus) -> None:
        await self.graph.query(
            "MATCH (t:Topic {id: $id}) SET t.status = $status",
            {"id": topic_id, "status": status.value},
        )

    async def update_explanation_level(self, topic_id: str, level: int) -> None:
        await self.graph.query(
            "MATCH (t:Topic {id: $id}) SET t.explanation_level = $level",
            {"id": topic_id, "level": level},
        )

    async def mark_content_ready(self, topic_id: str) -> None:
        await self.graph.query(
            "MATCH (t:Topic {id: $id}) SET t.content_ready = true",
            {"id": topic_id},
        )

    async def list_all(self) -> list[dict]:
        result = await self.graph.query(
            """
            MATCH (t:Topic)
            OPTIONAL MATCH (t)-[:REQUIRES]->(req:Topic)
            RETURN t, collect(req.id) AS prereqs
            """
        )
        out = []
        for row in result.result_set:
            props = dict(row[0].properties)
            props["prereqs"] = [p for p in row[1] if p]
            out.append(props)
        return out

    async def find_newly_unlockable(self, mastered_topic_id: str) -> list[str]:
        """
        After a topic is mastered, find locked topics whose every REQUIRES
        dependency is now mastered. Returns their IDs.
        """
        result = await self.graph.query(
            """
            MATCH (candidate:Topic {status: 'locked'})-[:REQUIRES]->(req:Topic)
            WITH candidate, collect(req.status) AS req_statuses
            WHERE ALL(s IN req_statuses WHERE s = 'mastered')
            RETURN candidate.id
            """,
        )
        return [row[0] for row in result.result_set]
