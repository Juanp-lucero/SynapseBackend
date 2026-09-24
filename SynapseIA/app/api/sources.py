import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File
)

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.source import Source
from app.models.project import Project
from app.models.user import User
from app.schemas.source import SourceCreate, SourceResponse
from app.core.security import get_current_user
from app.services.document_processor import process_document


router = APIRouter(
    prefix="/sources",
    tags=["Sources"]
)


# =========================
# Configuración de archivos
# =========================

UPLOAD_DIR = "uploads"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".csv"
}


# =========================
# Crear fuente
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
# Subir archivo
# =========================

@router.post(
    "/upload",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_source(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # =========================
    # Verificar proyecto
    # =========================

    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )


    # =========================
    # Obtener extensión
    # =========================

    original_name = file.filename or ""

    extension = os.path.splitext(
        original_name
    )[1].lower()


    # =========================
    # Validar extensión
    # =========================

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Use PDF, TXT, DOCX o CSV."
        )


    # =========================
    # Crear carpeta
    # =========================

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )


    # =========================
    # Crear nombre único
    # =========================

    unique_name = (
        f"{uuid.uuid4()}{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_name
    )


    # =========================
    # Guardar archivo
    # =========================

    with open(
        file_path,
        "wb"
    ) as buffer:

        content = await file.read()

        buffer.write(content)


    # =========================
    # Extraer texto
    # =========================

    try:

        extracted_text = process_document(
            file_path
        )

    except Exception as e:

        extracted_text = ""

        print(
            f"Error procesando documento: {e}"
        )


    # =========================
    # Crear registro
    # =========================

    source = Source(
        name=original_name,
        type=extension.replace(
            ".",
            ""
        ).upper(),
        description=f"Archivo cargado: {original_name}",
        file_path=file_path,
        extracted_text=extracted_text,
        project_id=project.id
    )


    # =========================
    # Guardar en PostgreSQL
    # =========================

    db.add(source)

    db.commit()

    db.refresh(source)


    return source


# =========================
# Listar fuentes
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
# Obtener una fuente
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
# Eliminar fuente
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


    # =========================
    # Eliminar archivo físico
    # =========================

    if source.file_path:

        if os.path.exists(
            source.file_path
        ):

            os.remove(
                source.file_path
            )


    # =========================
    # Eliminar registro
    # =========================

    db.delete(source)

    db.commit()


    return {
        "message": "Fuente eliminada correctamente"
    }