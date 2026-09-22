from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.core.security import get_current_user


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


@router.post(
    "/",
    response_model=ProjectResponse
)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    project = Project(
        name=project_data.name,
        description=project_data.description,
        user_id=current_user.id
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project