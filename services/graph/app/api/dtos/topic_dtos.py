from typing import Literal

from pydantic import BaseModel, Field

from app.domain.topic import TopicStatus


class CreateTopicRequest(BaseModel):
    name: str
    slug: str
    domain: str
    description: str
    complexity: int = Field(ge=1, le=10)
    status: TopicStatus = TopicStatus.LOCKED


class TopicTransitionRequest(BaseModel):
    action: Literal["open", "master", "escalate"]


class TopicResponse(BaseModel):
    id: str
    name: str
    slug: str
    domain: str
    description: str
    complexity: int
    status: str
    explanation_level: int
    content_ready: bool
    prereqs: list[str] = []
