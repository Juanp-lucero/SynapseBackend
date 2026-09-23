from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.source import Source
from app.models.project import Project
from app.models.user import User
from app.schemas.source import SourceCreate, SourceResponse
from app.core.security import get_current_user


router = APIRouter(
    prefix="/sources",
    tags=["Sources"]
)


# =========================
# CREAR FUENTE
# =========================

@router.post(
    "/",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_source(
    source_data: SourceCreate,
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    source = Source(
        name=source_data.name,
        type=source_data.type,
        description=source_data.description,
        file_path=source_data.file_path,
        project_id=project.id
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


# =========================
# LISTAR FUENTES
# =========================

@router.get(
    "/",
    response_model=list[SourceResponse]
)
def get_sources(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    sources = db.query(Source).filter(
        Source.project_id == project_id
    ).all()

    return sources


# =========================
# OBTENER UNA FUENTE
# =========================

@router.get(
    "/{source_id}",
    response_model=SourceResponse
)
def get_source(
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

    return source


# =========================
# ELIMINAR FUENTE
# =========================

@router.delete(
    "/{source_id}"
)
def delete_source(
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

    db.delete(source)
    db.commit()

    return {
        "message": "Fuente eliminada correctamente"
    }