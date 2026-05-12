import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from app.sources.base import BaseSource
from app.sources.models import CourseResult, SourceTopic

_BASE_URL = "https://ocw.mit.edu"
_SITEMAP_URL = "https://ocw.mit.edu/sitemap.xml"
_COURSES_PREFIX = "/courses/"

# Matches /courses/<course-id>/ with nothing after (top-level course URL)
_COURSE_URL_RE = re.compile(r"/courses/([^/]+)/$")


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _title_from_slug(slug: str) -> str:
    """Derive a human-readable title from a course slug like '18-01sc-single-variable-calculus-fall-2010'."""
    # Strip leading course number (e.g. '18-01sc-', '6-042j-')
    without_num = re.sub(r"^[\d]+-[\w]+-", "", slug)
    # Strip trailing semester suffix (e.g. '-fall-2010', '-spring-2005')
    without_sem = re.sub(r"-(fall|spring|summer|winter)-\d{4}$", "", without_num)
    return without_sem.replace("-", " ").title()


class MITOCWSource(BaseSource):
    source_id = "mit_ocw"
    display_name = "MIT OpenCourseWare"

    # Cached list of (course_id, title_hint) from sitemap
    _course_index: list[tuple[str, str]] | None = None

    async def _load_course_index(self) -> list[tuple[str, str]]:
        if self._course_index is not None:
            return self._course_index

        async with self._client() as client:
            resp = await client.get(_SITEMAP_URL)
            resp.raise_for_status()

        # sitemap.xml is a sitemapindex — each <loc> points to a per-course sitemap
        # e.g. https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/sitemap.xml
        # Course ID is embedded in the URL so no further requests are needed.
        root = ET.fromstring(resp.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # Match course sub-sitemap URLs
        _sub_re = re.compile(r"/courses/([^/]+)/sitemap\.xml$")

        seen: set[str] = set()
        index: list[tuple[str, str]] = []
        for loc in root.findall(".//sm:loc", ns):
            url = loc.text or ""
            m = _sub_re.search(url)
            if m:
                course_id = m.group(1)
                if course_id not in seen:
                    seen.add(course_id)
                    index.append((course_id, _title_from_slug(course_id)))

        self._course_index = index
        return index

    async def search(self, query: str, limit: int = 5) -> list[CourseResult]:
        index = await self._load_course_index()
        keywords = query.lower().split()

        matches: list[tuple[str, str]] = []
        for course_id, title in index:
            haystack = course_id.lower()
            if all(kw in haystack for kw in keywords):
                matches.append((course_id, title))
            if len(matches) >= limit:
                break

        return [
            CourseResult(
                source=self.source_id,
                course_id=course_id,
                title=title,
                description="",
                url=f"{_BASE_URL}{_COURSES_PREFIX}{course_id}/",
                domain=query,
            )
            for course_id, title in matches
        ]

    async def fetch_topics(self, course_id: str) -> CourseResult:
        course_url = f"{_BASE_URL}{_COURSES_PREFIX}{course_id}/"
        async with self._client() as client:
            resp = await client.get(course_url)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        title_el = soup.select_one("h1")
        title = title_el.get_text(strip=True) if title_el else _title_from_slug(course_id)

        desc_el = soup.select_one(".course-description, .course-info-description")
        description = desc_el.get_text(strip=True) if desc_el else ""

        topics = self._parse_topics(soup, course_id)

        return CourseResult(
            source=self.source_id,
            course_id=course_id,
            title=title,
            description=description,
            url=course_url,
            domain="",
            topics=topics,
        )

    def _parse_topics(self, soup: BeautifulSoup, course_id: str) -> list[SourceTopic]:
        """Extract top-level course sections from the course nav sidebar."""
        topics: list[SourceTopic] = []
        pages_prefix = f"{_COURSES_PREFIX}{course_id}/pages/"

        seen: set[str] = set()
        for i, a in enumerate(soup.select("nav a[href]")):
            href = a.get("href", "")
            if not href.startswith(pages_prefix):
                continue

            # Relative path after /pages/: e.g. "syllabus/" or "1.-differentiation/"
            rel = href[len(pages_prefix):].strip("/")
            if not rel or "/" in rel:
                # Skip sub-section links (they contain another slash)
                continue
            if rel in seen:
                continue
            seen.add(rel)

            title = a.get_text(strip=True)
            if not title:
                continue

            topics.append(SourceTopic(
                title=title,
                slug=_slugify(title),
                url=f"{_BASE_URL}{href}",
                order=i,
            ))

        return topics
