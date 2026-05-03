from pydantic import BaseModel


class GoogleCallbackRequest(BaseModel):
    code: str
    state: str | None = None
