import asyncio
import logging

from fastapi import HTTPException

from app.sources.models import CourseResult
from app.sources.registry import get_source, list_sources

log = logging.getLogger("material_service")


class MaterialService:
    def list_sources(self) -> list[dict]:
        sources = list_sources()
        log.debug("list_sources | count=%d", len(sources))
        return sources

    async def search(self, query: str, source_id: str, limit: int = 5) -> list[CourseResult]:
        log.info("search | source=%s query=%s limit=%d", source_id, query[:60], limit)
        try:
            source = get_source(source_id)
        except KeyError as e:
            log.warning("unknown source | id=%s", source_id)
            raise HTTPException(status_code=400, detail=str(e))
        results = await source.search(query, limit=limit)
        log.info("search done | source=%s results=%d", source_id, len(results))
        return results

    async def search_all(self, query: str, limit: int = 5) -> list[CourseResult]:
        log.info("search_all | query=%s limit=%d", query[:60], limit)
        tasks = [get_source(sid).search(query, limit=limit) for sid in ("mit_ocw", "khan_academy")]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        combined: list[CourseResult] = []
        for i, r in enumerate(results):
            source_id = ("mit_ocw", "khan_academy")[i]
            if isinstance(r, Exception):
                log.warning("search_all source failed | source=%s error=%s", source_id, r)
            else:
                log.debug("search_all partial | source=%s results=%d", source_id, len(r))
                combined.extend(r)
        log.info("search_all done | total=%d", len(combined))
        return combined

    async def fetch_topics(self, source_id: str, course_id: str) -> CourseResult:
        log.info("fetch_topics | source=%s course=%s", source_id, course_id)
        try:
            source = get_source(source_id)
        except KeyError as e:
            log.warning("unknown source | id=%s", source_id)
            raise HTTPException(status_code=400, detail=str(e))
        result = await source.fetch_topics(course_id)
        log.info("fetch_topics done | source=%s course=%s topics=%d",
                 source_id, course_id, len(result.subtopics) if result else 0)
        return result
