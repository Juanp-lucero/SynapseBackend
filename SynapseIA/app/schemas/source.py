from pydantic import BaseModel
from app.services.document_processor import process_document

class SourceCreate(BaseModel):

    name: str
    type: str
    description: str | None = None
    file_path: str | None = None


class SourceResponse(BaseModel):

    id: int
    name: str
    type: str
    description: str | None
    file_path: str | None
    extracted_text: str | None
    project_id: int

    class Config:
        from_attributes = True