"""Unit tests for the AI extraction validation (no network requests)."""

from app.core.config import settings
from app.services import ai_extractor
from app.services.ai_extractor import (
    extract_with_ai,
    merge_extraction,
    validate_extraction,
)

TEXT = (
    "Satya Nadella dirige Microsoft desde Seattle. "
    "Microsoft colabora con OpenAI en inteligencia artificial."
)


def test_entities_not_present_in_the_text_are_discarded() -> None:
    result = validate_extraction(
        TEXT,
        {
            "entities": [
                {"name": "Microsoft", "type": "ORGANIZATION"},
                {"name": "Google", "type": "ORGANIZATION"},
            ]
        },
    )
    assert [entity["value"] for entity in result["entities"]] == ["Microsoft"]


def test_unknown_entity_types_fall_back_to_concept() -> None:
    result = validate_extraction(
        TEXT, {"entities": [{"name": "OpenAI", "type": "COMPANY"}]}
    )
    assert result["entities"][0]["type"] == "CONCEPT"


def test_relations_require_two_validated_entities() -> None:
    result = validate_extraction(
        TEXT,
        {
            "entities": [
                {"name": "Satya Nadella", "type": "PERSON"},
                {"name": "Microsoft", "type": "ORGANIZATION"},
            ],
            "relations": [
                {"source": "Satya Nadella", "relation": "dirige", "target": "Microsoft"},
                {"source": "Microsoft", "relation": "compite con", "target": "Google"},
            ],
        },
    )
    assert result["relations"] == [
        {
            "source": "Satya Nadella",
            "relation": "DIRIGE",
            "target": "Microsoft",
            "evidence": "",
            "origin": "ai",
        }
    ]


def test_hypotheses_must_cite_validated_entities_and_clamp_confidence() -> None:
    result = validate_extraction(
        TEXT,
        {
            "entities": [{"name": "OpenAI", "type": "ORGANIZATION"}],
            "hypotheses": [
                {"title": "Alianza estratégica", "entities": ["OpenAI"], "confidence": 7},
                {"title": "Sin evidencia", "entities": ["Apple"], "confidence": 0.9},
            ],
        },
    )
    assert len(result["hypotheses"]) == 1
    assert result["hypotheses"][0]["title"] == "Alianza estratégica"
    assert result["hypotheses"][0]["confidence"] == 1.0


def test_extract_with_ai_returns_none_without_api_key(monkeypatch) -> None:
    monkeypatch.setattr(settings, "groq_api_key", "")
    assert extract_with_ai(TEXT) is None


def test_extract_with_ai_validates_model_output(monkeypatch) -> None:
    monkeypatch.setattr(settings, "groq_api_key", "fake-key")
    monkeypatch.setattr(
        ai_extractor,
        "generate_json",
        lambda **_: {
            "entities": [
                {"name": "Microsoft", "type": "ORGANIZATION"},
                {"name": "Inventada S.A.", "type": "ORGANIZATION"},
            ]
        },
    )
    result = extract_with_ai(TEXT)
    assert [entity["value"] for entity in result["entities"]] == ["Microsoft"]


def test_merge_keeps_rule_results_and_adds_ai_results_once() -> None:
    rules = {
        "entities": [{"type": "YEAR", "value": "2024"}],
        "relations": [],
        "patterns": [{"type": "GROWTH", "description": "..."}],
        "hypotheses": [],
    }
    ai = {
        "entities": [
            {"type": "ORGANIZATION", "value": "Microsoft"},
            {"type": "YEAR", "value": "2024"},
        ],
        "relations": [],
        "hypotheses": [],
    }
    merged = merge_extraction(rules, ai)
    assert [entity["value"] for entity in merged["entities"]] == [
        "Microsoft",
        "2024",
    ]
    assert merged["patterns"] == rules["patterns"]


def test_merge_without_ai_returns_rule_results_unchanged() -> None:
    rules = {"entities": [], "relations": [], "patterns": [], "hypotheses": []}
    assert merge_extraction(rules, None) is rules
