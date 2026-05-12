import re
from urllib.parse import quote_plus

from app.sources.base import BaseSource
from app.sources.models import CourseResult, SourceTopic

# Khan Academy content API (v2 content tree)
_API_BASE = "https://www.khanacademy.org/api/v2"
_CONTENT_BASE = "https://www.khanacademy.org/api/v1"

# Curated domain → KA topic slug mapping so AI can target subjects directly
_DOMAIN_SLUGS: dict[str, str] = {
    "chemistry": "chemistry",
    "biology": "biology",
    "physics": "physics",
    "math": "math",
    "algebra": "algebra",
    "calculus": "differential-calculus",
    "statistics": "statistics-probability",
    "computer science": "computing",
}


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


class KhanAcademySource(BaseSource):
    source_id = "khan_academy"
    display_name = "Khan Academy"

    async def search(self, query: str, limit: int = 5) -> list[CourseResult]:
        # KA doesn't have a public search API — resolve known domain slugs
        slug = _DOMAIN_SLUGS.get(query.lower())
        if not slug:
            # Best-effort: use the query as slug directly
            slug = _slugify(query)

        topic = await self._fetch_topic(slug)
        if not topic:
            return []

        # Each top-level child of the domain is treated as a "course"
        results: list[CourseResult] = []
        children = topic.get("children") or topic.get("child_data") or []
        for child in children[:limit]:
            if child.get("kind") not in ("Topic", "Course"):
                continue
            results.append(
                CourseResult(
                    source=self.source_id,
                    course_id=child.get("slug", ""),
                    title=child.get("title", ""),
                    description=child.get("description", ""),
                    url=f"https://www.khanacademy.org{child.get('url', '')}",
                    domain=query,
                )
            )
        return results

    async def fetch_topics(self, course_id: str) -> CourseResult:
        topic = await self._fetch_topic(course_id)
        if not topic:
            return CourseResult(
                source=self.source_id,
                course_id=course_id,
                title=course_id,
                description="",
                url=f"https://www.khanacademy.org/{course_id}",
                domain="",
                topics=[],
            )

        topics = self._extract_topics(topic.get("children") or topic.get("child_data") or [])

        return CourseResult(
            source=self.source_id,
            course_id=course_id,
            title=topic.get("title", course_id),
            description=topic.get("description", ""),
            url=f"https://www.khanacademy.org{topic.get('url', '')}",
            domain="",
            topics=topics,
        )

    async def _fetch_topic(self, slug: str) -> dict | None:
        url = f"{_CONTENT_BASE}/topic/{slug}"
        async with self._client() as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None
            return resp.json()

    def _extract_topics(self, children: list[dict], depth: int = 0) -> list[SourceTopic]:
        topics: list[SourceTopic] = []
        for i, child in enumerate(children):
            kind = child.get("kind", "")
            if kind not in ("Topic", "Course", "Exercise", "Article"):
                continue
            title = child.get("title", "")
            if not title:
                continue

            subtopics: list[SourceTopic] = []
            if depth < 2 and kind in ("Topic", "Course"):
                sub_children = child.get("children") or child.get("child_data") or []
                subtopics = self._extract_topics(sub_children, depth + 1)

            topics.append(
                SourceTopic(
                    title=title,
                    slug=child.get("slug", _slugify(title)),
                    description=child.get("description", ""),
                    url=f"https://www.khanacademy.org{child.get('url', '')}",
                    order=i,
                    subtopics=subtopics,
                )
            )
        return topics
