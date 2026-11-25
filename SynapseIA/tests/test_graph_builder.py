"""Unit tests for the PostgreSQL-backed Knowledge Graph builder."""

from types import SimpleNamespace

from app.services.graph_builder import build_graph_from_analyses


def make_source(source_id: int, name: str) -> SimpleNamespace:
    return SimpleNamespace(id=source_id, name=name)


def make_analysis(entities, relations=None, patterns=None, hypotheses=None):
    return SimpleNamespace(
        entities=entities,
        relations=relations or [],
        patterns=patterns or [],
        hypotheses=hypotheses or [],
    )


def relation_names(graph: dict) -> set[str]:
    return {item["relation"] for item in graph["relationships"]}


def test_empty_sources_return_empty_graph() -> None:
    graph = build_graph_from_analyses([], {})
    assert graph == {"source_ids": [], "nodes": [], "relationships": []}


def test_source_without_analysis_is_still_a_document_node() -> None:
    graph = build_graph_from_analyses([make_source(1, "informe.pdf")], {})
    assert graph["source_ids"] == [1]
    assert graph["nodes"] == [
        {
            "labels": ["Document"],
            "properties": {"source_id": 1, "name": "informe.pdf"},
        }
    ]
    assert graph["relationships"] == []


def test_entities_relations_patterns_and_hypotheses_become_nodes() -> None:
    analysis = make_analysis(
        entities=[
            {"type": "ORGANIZATION", "value": "Microsoft"},
            {"type": "PERSON", "value": "Satya Nadella"},
        ],
        relations=[
            {"source": "Satya Nadella", "relation": "DIRIGE", "target": "Microsoft"}
        ],
        patterns=[{"type": "GROWTH", "description": "Crecimiento de ventas"}],
        hypotheses=[{"title": "Liderazgo", "description": "...", "confidence": 0.7}],
    )
    graph = build_graph_from_analyses(
        [make_source(1, "a.txt")], {1: analysis}
    )

    labels = sorted(node["labels"][0] for node in graph["nodes"])
    assert labels == ["Document", "Entity", "Entity", "Hypothesis", "Pattern"]
    assert {"MENTIONED_IN", "DIRIGE", "DETECTED_IN", "GENERATED_FROM"} <= (
        relation_names(graph)
    )


def test_duplicate_entities_are_merged_case_insensitively() -> None:
    analysis = make_analysis(
        entities=[
            {"type": "ORGANIZATION", "value": "OpenAI"},
            {"type": "organization", "value": "openai"},
        ]
    )
    graph = build_graph_from_analyses(
        [make_source(1, "a.txt")], {1: analysis}
    )
    entities = [n for n in graph["nodes"] if n["labels"] == ["Entity"]]
    assert len(entities) == 1


def test_documents_sharing_entities_are_connected() -> None:
    first = make_analysis([{"type": "ORGANIZATION", "value": "Microsoft"}])
    second = make_analysis([{"type": "ORGANIZATION", "value": "microsoft"}])

    graph = build_graph_from_analyses(
        [make_source(1, "a.txt"), make_source(2, "b.txt")],
        {1: first, 2: second},
    )

    shared = [
        item
        for item in graph["relationships"]
        if item["relation"] == "SHARES_ENTITIES_WITH"
    ]
    assert len(shared) == 1
    assert shared[0]["source"]["source_id"] == 1
    assert shared[0]["target"]["source_id"] == 2
    assert shared[0]["properties"]["shared_entities"] == ["microsoft"]


def test_numbers_and_years_do_not_link_documents() -> None:
    first = make_analysis([{"type": "YEAR", "value": "2024"}])
    second = make_analysis([{"type": "YEAR", "value": "2024"}])

    graph = build_graph_from_analyses(
        [make_source(1, "a.txt"), make_source(2, "b.txt")],
        {1: first, 2: second},
    )

    assert "SHARES_ENTITIES_WITH" not in relation_names(graph)


def test_relations_to_unknown_entities_are_ignored() -> None:
    analysis = make_analysis(
        entities=[{"type": "ORGANIZATION", "value": "Microsoft"}],
        relations=[
            {"source": "Microsoft", "relation": "COMPITE_CON", "target": "Google"}
        ],
    )
    graph = build_graph_from_analyses(
        [make_source(1, "a.txt")], {1: analysis}
    )
    assert "COMPITE_CON" not in relation_names(graph)
