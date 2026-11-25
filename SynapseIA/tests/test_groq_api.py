"""API tests for authenticated Synapse AI endpoints."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import get_current_user
from app.database.connection import Base, get_db
from app.main import app
from app.models.user import User

TEST_USER = User(
    id=101,
    name="Synapse AI Test",
    email="synapse-ai-test@example.com",
    password="not-used",
)


@pytest.fixture
def client(monkeypatch) -> Generator[TestClient, None, None]:
    from app.core.config import settings

    monkeypatch.setattr(settings, "groq_api_key", "")
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_db():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: TEST_USER

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_ai_status_never_exposes_api_key(client: TestClient) -> None:
    response = client.get("/ai/status")
    assert response.status_code == 200
    assert response.json()["provider"] == "groq"
    assert response.json()["configured"] is False
    assert "api_key" not in response.json()


def test_ai_question_validates_body(client: TestClient) -> None:
    response = client.post(
        "/ai/source/1/ask",
        json={"question": "x"},
    )
    assert response.status_code == 422


def test_ai_summary_requires_owned_source(client: TestClient) -> None:
    response = client.post("/ai/source/999/summary")
    assert response.status_code == 404


def test_ai_question_requires_owned_source(client: TestClient) -> None:
    response = client.post(
        "/ai/source/999/ask",
        json={"question": "¿Qué relaciones se encontraron?"},
    )
    assert response.status_code == 404
