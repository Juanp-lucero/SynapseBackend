from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Relación con el usuario
    user = relationship(
        "User",
        back_populates="projects"
    )

    # Relación con las fuentes
    sources = relationship(
        "Source",
        back_populates="project",
        cascade="all, delete-orphan"
    )