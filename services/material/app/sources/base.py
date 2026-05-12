from abc import ABC, abstractmethod

import httpx
from settings import settings

from app.sources.models import CourseResult


class BaseSource(ABC):
    source_id: str
    display_name: str

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=settings.fetch_timeout, follow_redirects=True)

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> list[CourseResult]:
        """Search for courses matching the query. Returns lightweight results (no topics yet)."""

    @abstractmethod
    async def fetch_topics(self, course_id: str) -> CourseResult:
        """Fetch the full topic tree for a specific course."""
