import re

import httpx
from settings import settings

from app.sources.base import BaseSource
from app.sources.models import CourseResult, SourceTopic

_API_URL = "https://en.wikipedia.org/w/api.php"
_USER_AGENT = "PureStudy/1.0 (educational app; https://github.com/pure-study) httpx"


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


class WikipediaSource(BaseSource):
    source_id = "wikipedia"
    display_name = "Wikipedia"

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=settings.fetch_timeout,
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        )

    async def search(self, query: str, limit: int = 5) -> list[CourseResult]:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "0",
            "srlimit": str(limit),
            "srprop": "snippet",
            "format": "json",
        }
        async with self._client() as client:
            resp = await client.get(_API_URL, params=params)
            resp.raise_for_status()

        data = resp.json()
        results: list[CourseResult] = []
        for item in data.get("query", {}).get("search", []):
            title = item["title"]
            snippet = re.sub(r"<[^>]+>", "", item.get("snippet", ""))
            results.append(CourseResult(
                source=self.source_id,
                course_id=title.replace(" ", "_"),
                title=title,
                description=snippet,
                url=f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                domain=query,
            ))
        return results

    async def fetch_topics(self, course_id: str) -> CourseResult:
        """Fetch Wikipedia article sections as topics. course_id is the article title (underscores ok)."""
        article_title = course_id.replace("_", " ")

        params = {
            "action": "parse",
            "page": article_title,
            "prop": "sections|text",
            "sectionpreview": "1",
            "format": "json",
        }
        async with self._client() as client:
            resp = await client.get(_API_URL, params=params)
            resp.raise_for_status()

        data = resp.json()
        parse = data.get("parse", {})
        title = parse.get("title", article_title)

        topics: list[SourceTopic] = []
        for i, section in enumerate(parse.get("sections", [])):
            # Only top-level sections (toclevel 1 = h2)
            if section.get("toclevel", 0) != 1:
                continue
            section_title = section.get("line", "")
            if not section_title or section_title.lower() in (
                "see also", "references", "further reading", "external links",
                "notes", "bibliography", "citations",
            ):
                continue
            anchor = section.get("anchor", "")
            topics.append(SourceTopic(
                title=section_title,
                slug=_slugify(section_title),
                url=f"https://en.wikipedia.org/wiki/{course_id}#{anchor}",
                order=i,
            ))

        return CourseResult(
            source=self.source_id,
            course_id=course_id,
            title=title,
            description="",
            url=f"https://en.wikipedia.org/wiki/{course_id}",
            domain="",
            topics=topics,
        )
