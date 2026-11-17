from app.core.config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


if not settings.database_url:
    raise RuntimeError(
        "DATABASE_URL no está configurada. Revisa SynapseIA/.env."
    )

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
