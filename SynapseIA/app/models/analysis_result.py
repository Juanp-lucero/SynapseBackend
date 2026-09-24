from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.connection import Base


class AnalysisResult(Base):

    __tablename__ = "analysis_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    source_id = Column(
        Integer,
        ForeignKey("sources.id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="completed"
    )

    entities = Column(
        JSONB,
        nullable=False,
        default=list
    )

    relations = Column(
        JSONB,
        nullable=False,
        default=list
    )

    patterns = Column(
        JSONB,
        nullable=False,
        default=list
    )

    hypotheses = Column(
        JSONB,
        nullable=False,
        default=list
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    source = relationship(
        "Source",
        back_populates="analysis_results"
    )