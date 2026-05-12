import os

os.environ.setdefault("FETCH_TIMEOUT", "15")

import pytest


@pytest.fixture
def mit_sitemap_xml() -> str:
    """MIT OCW sitemap index — each entry points to a per-course sitemap."""
    return """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://ocw.mit.edu/sitemap-www.xml</loc></sitemap>
  <sitemap><loc>https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/sitemap.xml</loc></sitemap>
  <sitemap><loc>https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/sitemap.xml</loc></sitemap>
  <sitemap><loc>https://ocw.mit.edu/courses/6-001-structure-and-interpretation-fall-2005/sitemap.xml</loc></sitemap>
</sitemapindex>
"""


@pytest.fixture
def mit_course_html() -> str:
    """MIT OCW course page with nav sidebar containing top-level and sub-level links."""
    return """
    <html><body>
    <h1>Single Variable Calculus</h1>
    <p class="course-description">Comprehensive intro to calculus.</p>
    <nav>
      <a href="/courses/18-01sc-single-variable-calculus-fall-2010/pages/syllabus/">Syllabus</a>
      <a href="/courses/18-01sc-single-variable-calculus-fall-2010/pages/1-differentiation/">1. Differentiation</a>
      <a href="/courses/18-01sc-single-variable-calculus-fall-2010/pages/1-differentiation/part-a/">Part A: Basic Rules</a>
      <a href="/courses/18-01sc-single-variable-calculus-fall-2010/pages/2-integration/">2. Integration</a>
      <a href="/courses/18-01sc-single-variable-calculus-fall-2010/pages/2-integration/part-b/">Part B: Techniques</a>
    </nav>
    </body></html>
    """


@pytest.fixture
def wikipedia_search_response() -> dict:
    return {
        "query": {
            "search": [
                {
                    "title": "Calculus",
                    "snippet": "Branch of mathematics involving <span>derivatives</span> and integrals.",
                },
                {
                    "title": "Differential calculus",
                    "snippet": "Subfield of <span>calculus</span> concerning rates of change.",
                },
            ]
        }
    }


@pytest.fixture
def wikipedia_parse_response() -> dict:
    return {
        "parse": {
            "title": "Calculus",
            "sections": [
                {"toclevel": 1, "line": "History", "anchor": "History"},
                {"toclevel": 1, "line": "Principles", "anchor": "Principles"},
                {"toclevel": 2, "line": "Limits and infinitesimals", "anchor": "Limits"},
                {"toclevel": 1, "line": "Differential calculus", "anchor": "Differential_calculus"},
                {"toclevel": 1, "line": "Integral calculus", "anchor": "Integral_calculus"},
                {"toclevel": 1, "line": "See also", "anchor": "See_also"},
                {"toclevel": 1, "line": "References", "anchor": "References"},
            ],
        }
    }
