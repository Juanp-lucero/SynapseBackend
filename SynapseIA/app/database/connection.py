from app.core.config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


if not settings.database_url:
    raise RuntimeError(
        "DATABASE_URL no está configurada. Revisa SynapseIA/.env."
    )

# Serverless Postgres (Neon) closes idle connections; check each one before
# use and recycle them so a stale socket never reaches a request.
engine_options = {}
if not settings.database_url.startswith("sqlite"):
    engine_options = {"pool_pre_ping": True, "pool_recycle": 280}

engine = create_engine(settings.database_url, **engine_options)

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
