from fastapi import Depends

from app.api.dtos.material_dtos import CourseResultOut, SearchRequest
from app.services.material_service import MaterialService


def _get_service() -> MaterialService:
    return MaterialService()


class MaterialHandler:
    async def list_sources(
        self,
        svc: MaterialService = Depends(_get_service),
    ) -> list[dict]:
        return svc.list_sources()

    async def search(
        self,
        body: SearchRequest,
        svc: MaterialService = Depends(_get_service),
    ) -> list[CourseResultOut]:
        if body.source_id:
            results = await svc.search(body.query, body.source_id, body.limit)
        else:
            results = await svc.search_all(body.query, body.limit)
        return [CourseResultOut(**vars(r)) for r in results]

    async def fetch_topics(
        self,
        source_id: str,
        course_id: str,
        svc: MaterialService = Depends(_get_service),
    ) -> CourseResultOut:
        result = await svc.fetch_topics(source_id, course_id)
        return CourseResultOut(**vars(result))
