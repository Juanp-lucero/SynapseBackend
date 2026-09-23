from pydantic import BaseModel


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
    project_id: int

    class Config:
        from_attributes = True