from typing import Literal

from pydantic import BaseModel


class CreateEdgeRequest(BaseModel):
    from_id: str
    to_id: str
    edge_type: Literal["CONTAINS", "SUBTOPIC_OF", "REQUIRES", "RELATED_TO", "EQUIVALENT_TO"]


class DeleteEdgeRequest(BaseModel):
    from_id: str
    to_id: str
    edge_type: Literal["CONTAINS", "SUBTOPIC_OF", "REQUIRES", "RELATED_TO", "EQUIVALENT_TO"]
