from dataclasses import dataclass, field


@dataclass
class SourceTopic:
    title: str
    slug: str
    description: str = ""
    url: str = ""
    order: int = 0
    subtopics: list["SourceTopic"] = field(default_factory=list)


@dataclass
class CourseResult:
    source: str
    course_id: str
    title: str
    description: str
    url: str
    domain: str
    topics: list[SourceTopic] = field(default_factory=list)
