from fastapi import Depends, Header, HTTPException

from app.api.dtos.course_dtos import (
    CourseResponse,
    CourseWithTopicsResponse,
    CreateCourseRequest,
)
from app.api.dtos.edge_dtos import CreateEdgeRequest, DeleteEdgeRequest
from app.api.dtos.topic_dtos import (
    CreateTopicRequest,
    TopicResponse,
    TopicTransitionRequest,
)
from app.falkordb.session import get_user_graph
from app.services.graph_service import GraphService


def _get_service(x_user_id: str = Header(...)) -> GraphService:
    return GraphService(get_user_graph(x_user_id))


class GraphHandler:
    # ── Courses ───────────────────────────────────────────────────────────────

    async def create_course(
        self,
        body: CreateCourseRequest,
        svc: GraphService = Depends(_get_service),
    ) -> CourseResponse:
        return await svc.create_course(body.name, body.goal, body.domain)

    async def get_course(
        self,
        course_id: str,
        svc: GraphService = Depends(_get_service),
    ) -> CourseWithTopicsResponse:
        return await svc.get_course(course_id)

    async def list_courses(
        self,
        svc: GraphService = Depends(_get_service),
    ) -> list[CourseResponse]:
        return await svc.list_courses()

    # ── Topics ────────────────────────────────────────────────────────────────

    async def list_topics(
        self,
        svc: GraphService = Depends(_get_service),
    ) -> list[TopicResponse]:
        return await svc.list_all_topics()

    async def create_topic(
        self,
        body: CreateTopicRequest,
        svc: GraphService = Depends(_get_service),
    ) -> TopicResponse:
        return await svc.create_topic(
            name=body.name,
            slug=body.slug,
            domain=body.domain,
            description=body.description,
            complexity=body.complexity,
            status=body.status,
        )

    async def get_topic(
        self,
        topic_id: str,
        svc: GraphService = Depends(_get_service),
    ) -> TopicResponse:
        return await svc.get_topic(topic_id)

    async def get_available_topics(
        self,
        svc: GraphService = Depends(_get_service),
    ) -> list[TopicResponse]:
        return await svc.get_available_topics()

    async def transition_topic(
        self,
        topic_id: str,
        body: TopicTransitionRequest,
        svc: GraphService = Depends(_get_service),
    ) -> dict:
        if body.action == "open":
            return await svc.open_topic(topic_id)
        if body.action == "master":
            return await svc.master_topic(topic_id)
        if body.action == "escalate":
            return await svc.escalate_explanation(topic_id)
        raise HTTPException(status_code=400, detail=f"Unknown action '{body.action}'")

    async def mark_content_ready(
        self,
        topic_id: str,
        svc: GraphService = Depends(_get_service),
    ) -> dict:
        await svc.mark_content_ready(topic_id)
        return {"ok": True}

    # ── Edges ─────────────────────────────────────────────────────────────────

    async def create_edge(
        self,
        body: CreateEdgeRequest,
        svc: GraphService = Depends(_get_service),
    ) -> dict:
        await svc.create_edge(body.from_id, body.to_id, body.edge_type)
        return {"ok": True}

    async def delete_edge(
        self,
        body: DeleteEdgeRequest,
        svc: GraphService = Depends(_get_service),
    ) -> dict:
        await svc.delete_edge(body.from_id, body.to_id, body.edge_type)
        return {"ok": True}
