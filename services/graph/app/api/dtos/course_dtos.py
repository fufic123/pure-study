from pydantic import BaseModel


class CreateCourseRequest(BaseModel):
    name: str
    goal: str
    domain: str


class CourseResponse(BaseModel):
    id: str
    name: str
    goal: str
    domain: str


class CourseWithTopicsResponse(CourseResponse):
    topics: list[dict]
