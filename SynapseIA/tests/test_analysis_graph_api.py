"""API tests for the upload -> analysis -> knowledge graph flow."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import sources as sources_api
from app.core.config import settings
from app.core.security import get_current_user
from app.database.connection import Base, get_db
from app.main import app
from app.models.project import Project
from app.models.user import User

DOCUMENTS = {
    "ventas.txt": (
        "Las ventas de tecnología crecieron 30% en 2024. "
        "Los clientes aumentaron en todas las regiones."
    ),
    "informe.txt": (
        "El informe de ventas de 2023 muestra más clientes "
        "y nuevos productos."
    ),
}


@pytest.fixture
def client(monkeypatch, tmp_path) -> Generator[TestClient, None, None]:
    monkeypatch.setattr(settings, "groq_api_key", "")
    monkeypatch.setattr(sources_api, "UPLOAD_DIR", str(tmp_path))

    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with SessionTesting() as db:
        user = User(name="Ana", email="ana@example.com", password="not-used")
        db.add(user)
        db.commit()
        db.refresh(user)
        db.add(Project(name="Demo", description="Proyecto de prueba", user_id=user.id))
        db.commit()
        test_user = User(id=user.id, name=user.name, email=user.email)

    def override_db():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: test_user

    try:
        with TestClient(app) as test_client:
            test_client.upload_dir = tmp_path
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def upload(client: TestClient, name: str, text: str) -> int:
    response = client.post(
        "/sources/upload?project_id=1",
        files={"file": (name, text.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_analysis_uses_stored_text_when_upload_is_gone(client: TestClient) -> None:
    source_id = upload(client, "ventas.txt", DOCUMENTS["ventas.txt"])

    for path in client.upload_dir.iterdir():
        os.remove(path)

    response = client.post(f"/analysis/source/{source_id}")
    assert response.status_code == 201, response.text
    values = {entity["value"] for entity in response.json()["entities"]}
    assert "2024" in values


def test_graph_is_available_without_neo4j(client: TestClient) -> None:
    source_id = upload(client, "ventas.txt", DOCUMENTS["ventas.txt"])
    client.post(f"/analysis/source/{source_id}")

    for path in ("/graph", "/graph/", "/graph/project/1", f"/graph/source/{source_id}"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 200, (path, response.text)
        assert response.json()["nodes"], path


def test_project_graph_links_documents_with_shared_entities(
    client: TestClient,
) -> None:
    for name, text in DOCUMENTS.items():
        source_id = upload(client, name, text)
        assert client.post(f"/analysis/source/{source_id}").status_code == 201

    graph = client.get("/graph/project/1").json()
    relations = {item["relation"] for item in graph["relationships"]}
    assert "SHARES_ENTITIES_WITH" in relations


def test_graph_of_unknown_project_is_not_found(client: TestClient) -> None:
    assert client.get("/graph/project/999").status_code == 404
