from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.sources.mit_ocw import MITOCWSource
from app.sources.wikipedia import WikipediaSource


# ── MIT OCW ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mit_ocw_search_returns_matching_courses(mit_sitemap_xml):
    source = MITOCWSource()
    mock_resp = MagicMock(status_code=200, text=mit_sitemap_xml)
    mock_resp.raise_for_status = MagicMock()

    with patch.object(source, "_client") as mock_client_ctor:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_ctor.return_value = mock_client

        results = await source.search("calculus", limit=5)

    assert len(results) == 2
    ids = [r.course_id for r in results]
    assert "18-01sc-single-variable-calculus-fall-2010" in ids
    assert "18-02sc-multivariable-calculus-fall-2010" in ids
    assert all(r.source == "mit_ocw" for r in results)


@pytest.mark.asyncio
async def test_mit_ocw_search_respects_limit(mit_sitemap_xml):
    source = MITOCWSource()
    mock_resp = MagicMock(status_code=200, text=mit_sitemap_xml)
    mock_resp.raise_for_status = MagicMock()

    with patch.object(source, "_client") as mock_client_ctor:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_ctor.return_value = mock_client

        results = await source.search("calculus", limit=1)

    assert len(results) == 1


@pytest.mark.asyncio
async def test_mit_ocw_search_uses_cached_index(mit_sitemap_xml):
    source = MITOCWSource()
    mock_resp = MagicMock(status_code=200, text=mit_sitemap_xml)
    mock_resp.raise_for_status = MagicMock()

    with patch.object(source, "_client") as mock_client_ctor:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_ctor.return_value = mock_client

        await source.search("calculus")
        await source.search("calculus")

    # Sitemap fetched only once despite two calls
    assert mock_client.get.call_count == 1


@pytest.mark.asyncio
async def test_mit_ocw_fetch_topics_parses_top_level_nav(mit_course_html):
    source = MITOCWSource()
    mock_resp = MagicMock(status_code=200, text=mit_course_html)
    mock_resp.raise_for_status = MagicMock()

    with patch.object(source, "_client") as mock_client_ctor:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_ctor.return_value = mock_client

        result = await source.fetch_topics("18-01sc-single-variable-calculus-fall-2010")

    assert result.title == "Single Variable Calculus"
    topic_titles = [t.title for t in result.topics]
    assert "Syllabus" in topic_titles
    assert "1. Differentiation" in topic_titles
    assert "2. Integration" in topic_titles
    # Sub-section links must be excluded
    assert "Part A: Basic Rules" not in topic_titles
    assert "Part B: Techniques" not in topic_titles


# ── Wikipedia ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_wikipedia_search_returns_results(wikipedia_search_response):
    source = WikipediaSource()

    with patch.object(source, "_client") as mock_client_ctor:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value=wikipedia_search_response)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_ctor.return_value = mock_client

        results = await source.search("calculus", limit=5)

    assert len(results) == 2
    assert results[0].title == "Calculus"
    assert results[0].course_id == "Calculus"
    assert results[0].source == "wikipedia"
    # HTML tags stripped from snippet
    assert "<span>" not in results[0].description


@pytest.mark.asyncio
async def test_wikipedia_fetch_topics_returns_top_level_sections(wikipedia_parse_response):
    source = WikipediaSource()

    with patch.object(source, "_client") as mock_client_ctor:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value=wikipedia_parse_response)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_ctor.return_value = mock_client

        result = await source.fetch_topics("Calculus")

    assert result.title == "Calculus"
    titles = [t.title for t in result.topics]
    # Top-level sections included
    assert "History" in titles
    assert "Principles" in titles
    assert "Differential calculus" in titles
    assert "Integral calculus" in titles
    # Sub-sections excluded (toclevel > 1)
    assert "Limits and infinitesimals" not in titles
    # Boilerplate sections excluded
    assert "See also" not in titles
    assert "References" not in titles


@pytest.mark.asyncio
async def test_wikipedia_fetch_topics_slugs(wikipedia_parse_response):
    source = WikipediaSource()

    with patch.object(source, "_client") as mock_client_ctor:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value=wikipedia_parse_response)
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_ctor.return_value = mock_client

        result = await source.fetch_topics("Calculus")

    slugs = {t.slug for t in result.topics}
    assert "history" in slugs
    assert "differential-calculus" in slugs
