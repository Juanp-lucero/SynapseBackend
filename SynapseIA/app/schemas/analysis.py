from pydantic import BaseModel
from datetime import datetime


class AnalysisResponse(BaseModel):

    id: int
    source_id: int
    status: str
    entities: list
    relations: list
    patterns: list
    hypotheses: list
    created_at: datetime

    class Config:
        from_attributes = True