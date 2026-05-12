import logging

from fastapi import HTTPException

from app.domain.topic import Topic, TopicStatus
from app.falkordb.course_repo import CourseRepository
from app.falkordb.edge_repo import EdgeRepository
from app.falkordb.topic_repo import TopicRepository

log = logging.getLogger("graph_service")


class GraphService:
    def __init__(self, graph) -> None:
        self.courses = CourseRepository(graph)
        self.topics = TopicRepository(graph)
        self.edges = EdgeRepository(graph)

    # ── Courses ──────────────────────────────────────────────────────────────

    async def create_course(self, name: str, goal: str, domain: str) -> dict:
        log.debug("create_course | name=%s domain=%s", name, domain)
        result = await self.courses.create(name, goal, domain)
        log.info("course created | id=%s name=%s", result["id"], name)
        return result

    async def get_course(self, course_id: str) -> dict:
        log.debug("get_course | id=%s", course_id)
        course = await self.courses.get(course_id)
        if not course:
            log.warning("course not found | id=%s", course_id)
            raise HTTPException(status_code=404, detail="Course not found")
        topics = await self.topics.list_by_course(course_id)
        log.debug("course fetched | id=%s topics=%d", course_id, len(topics))
        return {**course, "topics": topics}

    async def list_courses(self) -> list[dict]:
        result = await self.courses.list_all()
        log.debug("list_courses | count=%d", len(result))
        return result

    # ── Topics ────────────────────────────────────────────────────────────────

    async def create_topic(
        self,
        name: str,
        slug: str,
        domain: str,
        description: str,
        complexity: int,
        status: TopicStatus = TopicStatus.LOCKED,
    ) -> dict:
        log.debug("create_topic | name=%s slug=%s complexity=%d status=%s", name, slug, complexity, status.value)
        result = await self.topics.create(name, slug, domain, description, complexity, status)
        log.info("topic created | id=%s name=%s", result["id"], name)
        return result

    async def get_topic(self, topic_id: str) -> dict:
        log.debug("get_topic | id=%s", topic_id)
        topic = await self.topics.get(topic_id)
        if not topic:
            log.warning("topic not found | id=%s", topic_id)
            raise HTTPException(status_code=404, detail="Topic not found")
        return topic

    async def list_all_topics(self) -> list[dict]:
        result = await self.topics.list_all()
        log.debug("list_all_topics | count=%d", len(result))
        return result

    async def get_available_topics(self) -> list[dict]:
        result = await self.topics.list_by_status(TopicStatus.AVAILABLE)
        log.debug("get_available_topics | count=%d", len(result))
        return result

    async def mark_content_ready(self, topic_id: str) -> None:
        topic = await self.topics.get(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        await self.topics.mark_content_ready(topic_id)
        log.info("topic content_ready=true | id=%s", topic_id)

    # ── State transitions ─────────────────────────────────────────────────────

    async def open_topic(self, topic_id: str) -> dict:
        data = await self._get_topic_or_404(topic_id)
        entity = self._to_entity(data)
        log.debug("open_topic | id=%s current_status=%s", topic_id, entity.status.value)
        try:
            entity.open()
        except ValueError as e:
            log.warning("open_topic rejected | id=%s | %s", topic_id, e)
            raise HTTPException(status_code=409, detail=str(e))
        await self.topics.update_status(topic_id, entity.status)
        log.info("topic opened | id=%s name=%s", topic_id, data["name"])
        return {**data, "status": entity.status.value}

    async def master_topic(self, topic_id: str) -> dict:
        data = await self._get_topic_or_404(topic_id)
        entity = self._to_entity(data)
        log.debug("master_topic | id=%s current_status=%s", topic_id, entity.status.value)
        try:
            entity.master()
        except ValueError as e:
            log.warning("master_topic rejected | id=%s | %s", topic_id, e)
            raise HTTPException(status_code=409, detail=str(e))
        await self.topics.update_status(topic_id, entity.status)

        unlockable_ids = await self.topics.find_newly_unlockable(topic_id)
        for dep_id in unlockable_ids:
            await self.topics.update_status(dep_id, TopicStatus.AVAILABLE)
            log.info("topic unlocked | id=%s (prereq %s mastered)", dep_id, topic_id)

        log.info("topic mastered | id=%s name=%s | unlocked=%d", topic_id, data["name"], len(unlockable_ids))
        return {**data, "status": entity.status.value, "unlocked": unlockable_ids}

    async def escalate_explanation(self, topic_id: str) -> dict:
        data = await self._get_topic_or_404(topic_id)
        entity = self._to_entity(data)
        try:
            entity.escalate_explanation()
        except ValueError as e:
            log.warning("escalate rejected | id=%s | %s", topic_id, e)
            raise HTTPException(status_code=409, detail=str(e))
        await self.topics.update_explanation_level(topic_id, entity.explanation_level)
        log.info("explanation escalated | id=%s level=%d", topic_id, entity.explanation_level)
        return {**data, "explanation_level": entity.explanation_level}

    # ── Edges ─────────────────────────────────────────────────────────────────

    async def create_edge(self, from_id: str, to_id: str, edge_type: str) -> None:
        log.debug("create_edge | %s -[%s]-> %s", from_id, edge_type, to_id)
        try:
            await self.edges.create(from_id, to_id, edge_type)
        except ValueError as e:
            log.warning("create_edge failed | %s", e)
            raise HTTPException(status_code=400, detail=str(e))
        log.info("edge created | %s -[%s]-> %s", from_id, edge_type, to_id)

    async def delete_edge(self, from_id: str, to_id: str, edge_type: str) -> None:
        log.debug("delete_edge | %s -[%s]-> %s", from_id, edge_type, to_id)
        try:
            await self.edges.delete(from_id, to_id, edge_type)
        except ValueError as e:
            log.warning("delete_edge failed | %s", e)
            raise HTTPException(status_code=400, detail=str(e))
        log.info("edge deleted | %s -[%s]-> %s", from_id, edge_type, to_id)

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _get_topic_or_404(self, topic_id: str) -> dict:
        data = await self.topics.get(topic_id)
        if not data:
            log.warning("topic not found | id=%s", topic_id)
            raise HTTPException(status_code=404, detail="Topic not found")
        return data

    @staticmethod
    def _to_entity(data: dict) -> Topic:
        return Topic(
            id=data["id"],
            name=data["name"],
            slug=data["slug"],
            domain=data["domain"],
            status=TopicStatus(data["status"]),
            explanation_level=int(data["explanation_level"]),
            content_ready=bool(data["content_ready"]),
            description=data["description"],
            complexity=int(data["complexity"]),
        )
