"""Unit tests for Groq integration without real network requests."""

from types import SimpleNamespace

import pytest

import httpx
from groq import NotFoundError

from app.core.config import settings
from app.services import groq_service


@pytest.fixture(autouse=True)
def reset_working_model(monkeypatch) -> None:
    monkeypatch.setattr(groq_service, "_working_model", None)


def test_summary_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr(settings, "groq_api_key", "")
    with pytest.raises(groq_service.GroqNotConfiguredError):
        groq_service.generate_analysis_summary(
            source_name="test.txt",
            entities=[],
            relations=[],
            patterns=[],
            hypotheses=[],
        )


def test_summary_uses_configured_model(monkeypatch) -> None:
    captured = {}
    monkeypatch.setattr(settings, "groq_api_key", "fake-key")
    monkeypatch.setattr(settings, "groq_model", "fake-model")

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Resumen fundamentado")
                    )
                ]
            )

    class FakeGroq:
        def __init__(self, api_key):
            captured["api_key"] = api_key
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(groq_service, "Groq", FakeGroq)

    result = groq_service.generate_analysis_summary(
        source_name="informe.pdf",
        entities=[{"name": "Entidad A"}],
        relations=[],
        patterns=[],
        hypotheses=[],
    )

    assert result == "Resumen fundamentado"
    assert captured["api_key"] == "fake-key"
    assert captured["model"] == "fake-model"
    assert captured["temperature"] == 0.2
    assert captured["timeout"] == 30


def test_question_answer_uses_supplied_question(monkeypatch) -> None:
    monkeypatch.setattr(settings, "groq_api_key", "fake-key")
    captured = {}

    def fake_generate(messages, max_tokens=1400):
        captured["messages"] = messages
        captured["max_tokens"] = max_tokens
        return "Respuesta de prueba"

    monkeypatch.setattr(groq_service, "_generate", fake_generate)

    answer = groq_service.answer_analysis_question(
        question="¿Qué relación existe?",
        source_name="documento.pdf",
        entities=[],
        relations=[{"source": "A", "target": "B"}],
        patterns=[],
        hypotheses=[],
    )

    assert answer == "Respuesta de prueba"
    assert "¿Qué relación existe?" in captured["messages"][1]["content"]
    assert captured["max_tokens"] == 1000


def test_provider_error_does_not_leak_provider_details(monkeypatch) -> None:
    monkeypatch.setattr(settings, "groq_api_key", "fake-key")

    class BrokenGroq:
        def __init__(self, api_key):
            raise RuntimeError("private provider detail")

    monkeypatch.setattr(groq_service, "Groq", BrokenGroq)

    with pytest.raises(groq_service.GroqServiceError) as error:
        groq_service.generate_analysis_summary(
            source_name="doc",
            entities=[],
            relations=[],
            patterns=[],
            hypotheses=[],
        )

    assert "private provider detail" not in str(error.value)


def test_prompt_treats_document_content_as_untrusted() -> None:
    assert "datos no confiables" in groq_service.SYSTEM_PROMPT
    assert "No inventes" in groq_service.SYSTEM_PROMPT


def model_not_found() -> NotFoundError:
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    return NotFoundError(
        "model_not_found", response=httpx.Response(404, request=request), body=None
    )


def test_retired_model_falls_back_to_the_next_one(monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(settings, "groq_api_key", "fake-key")
    monkeypatch.setattr(settings, "groq_model", "llama-3.3-70b-versatile")

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            if kwargs["model"] == "llama-3.3-70b-versatile":
                raise model_not_found()
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="Respuesta"))]
            )

    class FakeGroq:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(groq_service, "Groq", FakeGroq)

    result = groq_service.generate_analysis_summary(
        source_name="a.txt", entities=[], relations=[], patterns=[], hypotheses=[]
    )

    assert result == "Respuesta"
    assert [call["model"] for call in calls] == [
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-120b",
    ]
    # Reasoning models get extra budget and low effort so they still answer.
    assert calls[1]["extra_body"] == {"reasoning_effort": "low"}
    assert calls[1]["max_tokens"] > calls[0]["max_tokens"]
    assert groq_service.active_model() == "openai/gpt-oss-120b"


def test_error_when_no_model_is_available(monkeypatch) -> None:
    monkeypatch.setattr(settings, "groq_api_key", "fake-key")

    class FakeCompletions:
        def create(self, **kwargs):
            raise model_not_found()

    class FakeGroq:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(groq_service, "Groq", FakeGroq)

    with pytest.raises(groq_service.GroqServiceError):
        groq_service.generate_json(system_prompt="s", user_prompt="u")
