from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Source(Base):

    __tablename__ = "sources"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    type = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    file_path = Column(
        String(500),
        nullable=True
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    project = relationship(
        "Project",
        back_populates="sources"
    )

    analysis_results = relationship(
    "AnalysisResult",
    back_populates="source",
    cascade="all, delete-orphan"
)