from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.source import Source
from app.models.project import Project
from app.models.user import User
from app.models.analysis_result import AnalysisResult
from app.schemas.analysis import AnalysisResponse
from app.core.security import get_current_user
from app.services.analysis_service import analyze_document
from app.services.graph_service import save_analysis_to_graph


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post(
    "/source/{source_id}",
    response_model=AnalysisResponse,
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

        result = analyze_document(
            source.file_path
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el documento: {str(e)}"
        )

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

    try:

        save_analysis_to_graph(
            source_id=source.id,
            source_name=source.name,
            entities=result["entities"],
            relations=result["relations"],
            patterns=result["patterns"],
            hypotheses=result["hypotheses"]
        )

    except Exception as e:

        print(
            f"Error guardando información en Neo4j: {e}"
        )

    return analysis


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

    analyses = db.query(
        AnalysisResult
    ).filter(
        AnalysisResult.source_id == source_id
    ).order_by(
        AnalysisResult.created_at.desc()
    ).all()

    return analyses