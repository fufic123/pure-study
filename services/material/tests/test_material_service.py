from unittest.mock import AsyncMock, patch

import pytest
from app.services.material_service import MaterialService
from app.sources.models import CourseResult, SourceTopic
from fastapi import HTTPException


def _course(source: str, course_id: str = "c1", title: str = "Chemistry") -> CourseResult:
    return CourseResult(
        source=source,
        course_id=course_id,
        title=title,
        description="A chemistry course.",
        url="https://example.com",
        domain="chemistry",
    )


@pytest.mark.asyncio
async def test_search_delegates_to_correct_source():
    svc = MaterialService()
    expected = [_course("mit_ocw")]

    with patch("app.services.material_service.get_source") as mock_get:
        mock_source = AsyncMock()
        mock_source.search = AsyncMock(return_value=expected)
        mock_get.return_value = mock_source

        results = await svc.search("chemistry", "mit_ocw")

    mock_get.assert_called_once_with("mit_ocw")
    assert results == expected


@pytest.mark.asyncio
async def test_search_unknown_source_raises_400():
    svc = MaterialService()

    with patch("app.services.material_service.get_source", side_effect=KeyError("Unknown source 'bad'")):
        with pytest.raises(HTTPException) as exc:
            await svc.search("chemistry", "bad_source")
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_search_all_aggregates_results_from_all_sources():
    svc = MaterialService()
    mit_results = [_course("mit_ocw", "m1", "MIT Chemistry")]
    wiki_results = [_course("wikipedia", "k1", "Wikipedia Chemistry")]

    with patch("app.services.material_service.get_source") as mock_get:
        def side_effect(sid):
            m = AsyncMock()
            m.search = AsyncMock(return_value=mit_results if sid == "mit_ocw" else wiki_results)
            return m
        mock_get.side_effect = side_effect

        results = await svc.search_all("chemistry")

    sources = {r.source for r in results}
    assert "mit_ocw" in sources
    assert "wikipedia" in sources


@pytest.mark.asyncio
async def test_search_all_ignores_failed_sources():
    """A source that raises should not bring down the whole search."""
    svc = MaterialService()

    with patch("app.services.material_service.get_source") as mock_get:
        def side_effect(sid):
            m = AsyncMock()
            if sid == "mit_ocw":
                m.search = AsyncMock(side_effect=Exception("OCW down"))
            else:
                m.search = AsyncMock(return_value=[_course("wikipedia")])
            return m
        mock_get.side_effect = side_effect

        results = await svc.search_all("chemistry")

    assert all(r.source == "wikipedia" for r in results)


@pytest.mark.asyncio
async def test_fetch_topics_returns_course_with_topics():
    svc = MaterialService()
    topic = SourceTopic(title="Atomic Structure", slug="atomic-structure")
    expected = _course("mit_ocw")
    expected.topics = [topic]

    with patch("app.services.material_service.get_source") as mock_get:
        mock_source = AsyncMock()
        mock_source.fetch_topics = AsyncMock(return_value=expected)
        mock_get.return_value = mock_source

        result = await svc.fetch_topics("mit_ocw", "5-111sc")

    assert result.topics[0].title == "Atomic Structure"


@pytest.mark.asyncio
async def test_list_sources_returns_both_whitelisted_sources():
    svc = MaterialService()
    sources = svc.list_sources()
    ids = {s["id"] for s in sources}
    assert "mit_ocw" in ids
    assert "wikipedia" in ids
