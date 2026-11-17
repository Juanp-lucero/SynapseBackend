from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.source import Source
from app.models.project import Project
from app.models.user import User
from app.models.analysis_result import AnalysisResult
from app.schemas.analysis import AnalysisResponse, AnalysisWithSummaryResponse
from app.core.security import get_current_user
from app.services.analysis_service import analyze_document
from app.services.graph_service import save_analysis_to_graph
from app.services.groq_service import (
    GroqNotConfiguredError,
    GroqServiceError,
    generate_analysis_summary,
)


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post(
    "/source/{source_id}",
    response_model=AnalysisWithSummaryResponse,
    status_code=status.HTTP_201_CREATED
)
def analyze_source(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    source = db.query(Source).join(
        Project
    ).filter(
        Source.id == source_id,
        Project.user_id == current_user.id
    ).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fuente no encontrada"
        )

    if not source.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fuente no tiene un archivo asociado"
        )

    try:
        result = analyze_document(source.file_path)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No fue posible procesar el documento"
        ) from None

    analysis = AnalysisResult(
        source_id=source.id,
        status="completed",
        entities=result["entities"],
        relations=result["relations"],
        patterns=result["patterns"],
        hypotheses=result["hypotheses"]
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # AI summary is optional. The deterministic extraction result is saved
    # even when Groq is not configured or its external service is unavailable.
    ai_summary = None
    ai_provider = None
    try:
        ai_summary = generate_analysis_summary(
            source_name=source.name,
            entities=result["entities"],
            relations=result["relations"],
            patterns=result["patterns"],
            hypotheses=result["hypotheses"],
        )
        ai_provider = "groq"
    except (GroqNotConfiguredError, GroqServiceError):
        ai_summary = None

    try:
        save_analysis_to_graph(
            source_id=source.id,
            source_name=source.name,
            entities=result["entities"],
            relations=result["relations"],
            patterns=result["patterns"],
            hypotheses=result["hypotheses"]
        )
    except Exception:
        # PostgreSQL remains the source of truth if the graph is unavailable.
        pass

    response = AnalysisWithSummaryResponse.model_validate(analysis)
    response.ai_summary = ai_summary
    response.ai_provider = ai_provider
    return response


@router.get(
    "/source/{source_id}",
    response_model=list[AnalysisResponse]
)
def get_source_analyses(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    source = db.query(Source).join(
        Project
    ).filter(
        Source.id == source_id,
        Project.user_id == current_user.id
    ).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fuente no encontrada"
        )

    return db.query(
        AnalysisResult
    ).filter(
        AnalysisResult.source_id == source_id
    ).order_by(
        AnalysisResult.created_at.desc()
    ).all()
