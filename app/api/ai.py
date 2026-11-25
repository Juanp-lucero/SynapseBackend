"""AI endpoints for asking evidence-grounded questions about source analyses."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.database.connection import get_db
from app.models.analysis_result import AnalysisResult
from app.models.project import Project
from app.models.source import Source
from app.models.user import User
from app.services.groq_service import (
    GroqNotConfiguredError,
    GroqServiceError,
    active_model,
    generate_analysis_summary,
    answer_analysis_question,
)

router = APIRouter(prefix="/ai", tags=["AI"])


class AnalysisSummaryResponse(BaseModel):
    source_id: int
    provider: str
    model: str
    summary: str


class AnalysisQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1200)


class AnalysisQuestionResponse(BaseModel):
    source_id: int
    provider: str
    model: str
    answer: str


@router.get("/status")
def ai_status(
    _current_user: User = Depends(get_current_user),
) -> dict[str, str | bool]:
    """Report AI configuration state without exposing credentials."""
    return {
        "provider": "groq",
        "configured": bool(settings.groq_api_key),
        "model": active_model(),
    }


@router.post(
    "/source/{source_id}/summary",
    response_model=AnalysisSummaryResponse,
)
def summarize_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisSummaryResponse:
    """Generate a fresh explanation from the latest stored source analysis."""
    source = (
        db.query(Source)
        .join(Project)
        .filter(
            Source.id == source_id,
            Project.user_id == current_user.id,
        )
        .first()
    )
    if source is None:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    analysis = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.source_id == source.id)
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="La fuente todavía no tiene un análisis guardado",
        )

    try:
        summary = generate_analysis_summary(
            source_name=source.name,
            entities=analysis.entities or [],
            relations=analysis.relations or [],
            patterns=analysis.patterns or [],
            hypotheses=analysis.hypotheses or [],
        )
    except GroqNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None
    except GroqServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None

    return AnalysisSummaryResponse(
        source_id=source.id,
        provider="groq",
        model=active_model(),
        summary=summary,
    )


@router.post(
    "/source/{source_id}/ask",
    response_model=AnalysisQuestionResponse,
)
def ask_about_source(
    source_id: int,
    payload: AnalysisQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalysisQuestionResponse:
    """Answer a question using only the latest structured analysis evidence."""
    source = (
        db.query(Source)
        .join(Project)
        .filter(
            Source.id == source_id,
            Project.user_id == current_user.id,
        )
        .first()
    )
    if source is None:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    analysis = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.source_id == source.id)
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )
    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="La fuente todavía no tiene un análisis guardado",
        )

    try:
        answer = answer_analysis_question(
            question=payload.question,
            source_name=source.name,
            entities=analysis.entities or [],
            relations=analysis.relations or [],
            patterns=analysis.patterns or [],
            hypotheses=analysis.hypotheses or [],
        )
    except GroqNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None
    except GroqServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None

    return AnalysisQuestionResponse(
        source_id=source.id,
        provider="groq",
        model=active_model(),
        answer=answer,
    )
