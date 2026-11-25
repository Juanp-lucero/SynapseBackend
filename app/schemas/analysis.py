from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisResponse(BaseModel):
    id: int
    source_id: int
    status: str
    entities: list
    relations: list
    patterns: list
    hypotheses: list
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisWithSummaryResponse(AnalysisResponse):
    ai_summary: str | None = None
    ai_provider: str | None = None
