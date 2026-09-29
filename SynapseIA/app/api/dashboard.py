from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.models.user import User
from app.models.project import Project
from app.models.source import Source
from app.models.analysis_result import AnalysisResult

from app.core.security import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    projects_count = db.query(
        func.count(Project.id)
    ).filter(
        Project.user_id == current_user.id
    ).scalar()

    sources_count = db.query(
        func.count(Source.id)
    ).join(
        Project,
        Source.project_id == Project.id
    ).filter(
        Project.user_id == current_user.id
    ).scalar()

    analyses_count = db.query(
        func.count(AnalysisResult.id)
    ).join(
        Source,
        AnalysisResult.source_id == Source.id
    ).join(
        Project,
        Source.project_id == Project.id
    ).filter(
        Project.user_id == current_user.id
    ).scalar()

    hypotheses_count = db.query(
        func.coalesce(
            func.sum(
                func.jsonb_array_length(
                    AnalysisResult.hypotheses
                )
            ),
            0
        )
    ).join(
        Source,
        AnalysisResult.source_id == Source.id
    ).join(
        Project,
        Source.project_id == Project.id
    ).filter(
        Project.user_id == current_user.id
    ).scalar()

    return {
        "projects": projects_count or 0,
        "sources": sources_count or 0,
        "analyses": analyses_count or 0,
        "hypotheses": int(hypotheses_count or 0)
    }


@router.get("/activity")
def get_dashboard_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    projects = db.query(
        Project
    ).filter(
        Project.user_id == current_user.id
    ).order_by(
        Project.id.desc()
    ).limit(5).all()

    sources = db.query(
        Source
    ).join(
        Project,
        Source.project_id == Project.id
    ).filter(
        Project.user_id == current_user.id
    ).order_by(
        Source.id.desc()
    ).limit(5).all()

    analyses = db.query(
        AnalysisResult
    ).join(
        Source,
        AnalysisResult.source_id == Source.id
    ).join(
        Project,
        Source.project_id == Project.id
    ).filter(
        Project.user_id == current_user.id
    ).order_by(
        AnalysisResult.id.desc()
    ).limit(5).all()


    activity = []


    for project in projects:

        activity.append({
            "type": "project",
            "title": project.name,
            "description": "Proyecto creado",
            "id": project.id
        })


    for source in sources:

        activity.append({
            "type": "source",
            "title": source.name,
            "description": "Fuente cargada",
            "id": source.id
        })


    for analysis in analyses:

        activity.append({
            "type": "analysis",
            "title": "Análisis completado",
            "description": (
                f"Análisis de la fuente "
                f"{analysis.source_id}"
            ),
            "id": analysis.id
        })


    return activity