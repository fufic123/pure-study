from pydantic import BaseModel


class OnboardingMessageRequest(BaseModel):
    history: list[dict] = []
    message: str


class OnboardingMessageResponse(BaseModel):
    reply: str
    done: bool
    course: dict | None = None


class ExplainRequest(BaseModel):
    topic_id: str
    level: int = 1
    history: list[dict] = []
    message: str | None = None


class ExplainResponse(BaseModel):
    text: str


class CopilotRequest(BaseModel):
    topic_id: str
    history: list[dict] = []
    message: str


class CopilotResponse(BaseModel):
    reply: str
    history: list[dict]


class NextLevelRequest(BaseModel):
    course_id: str
    mastered_topic_id: str
    subject: str
