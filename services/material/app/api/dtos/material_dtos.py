from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    source_id: str | None = None  # None → search all sources
    limit: int = Field(default=5, ge=1, le=20)


class SourceTopicOut(BaseModel):
    title: str
    slug: str
    description: str
    url: str
    order: int
    subtopics: list["SourceTopicOut"] = []


class CourseResultOut(BaseModel):
    source: str
    course_id: str
    title: str
    description: str
    url: str
    domain: str
    topics: list[SourceTopicOut] = []
