from fastapi import FastAPI

from app.database.connection import Base, engine
from app.models.user import User
from app.models.project import Project
from app.models.source import Source
from app.models.analysis_result import AnalysisResult
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.sources import router as sources_router
from app.api.analysis import router as analysis_router
from app.api.graph import router as graph_router



Base.metadata.create_all(bind=engine)


# =========================
# Aplicación FastAPI
# =========================

app = FastAPI(
    title="Synapse IA",
    description="Sistema inteligente para descubrimiento de relaciones y patrones",
    version="1.0.0"
)


# =========================
# Registrar routers
# =========================

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(sources_router)
app.include_router(analysis_router)
app.include_router(graph_router)

# =========================
# Endpoints generales
# =========================

@app.get("/")
def root():

    return {
        "message": "Synapse IA API funcionando",
        "version": "1.0.0"
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "system": "Synapse IA"
    }


@app.get("/database")
def database_test():

    try:

        with engine.connect():

            return {
                "status": "ok",
                "database": "PostgreSQL conectado"
            }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }