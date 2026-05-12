from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TopicStatus(str, Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    MASTERED = "mastered"


@dataclass
class Topic:
    id: str
    name: str
    slug: str
    domain: str
    status: TopicStatus
    explanation_level: int
    content_ready: bool
    description: str
    complexity: int
    embedding: Optional[list[float]] = field(default=None)

    def open(self) -> None:
        if self.status != TopicStatus.AVAILABLE:
            raise ValueError(f"Cannot open topic in status '{self.status}' — must be 'available'")
        self.status = TopicStatus.IN_PROGRESS

    def master(self) -> None:
        if self.status != TopicStatus.IN_PROGRESS:
            raise ValueError(f"Cannot master topic in status '{self.status}' — must be 'in_progress'")
        self.status = TopicStatus.MASTERED

    def unlock(self) -> None:
        if self.status != TopicStatus.LOCKED:
            raise ValueError(f"Cannot unlock topic in status '{self.status}' — must be 'locked'")
        self.status = TopicStatus.AVAILABLE

    def escalate_explanation(self) -> None:
        if self.explanation_level >= 3:
            raise ValueError("Already at maximum explanation level (3)")
        self.explanation_level += 1
