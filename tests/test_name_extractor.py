"""Rule-based proper name detection used when AI is not available."""

from app.services.analysis_service import analyze_text_with_rules
from app.services.name_extractor import extract_name_relations, extract_proper_names

TEXT = (
    "Gabriel García Márquez nació en Aracataca, Colombia en 1927. "
    "Trabajó para El Espectador en Bogotá. "
    "La Universidad Nacional de Colombia lo homenajeó en 1982."
)


def test_detects_multiword_names_and_organizations() -> None:
    names = {entity["value"]: entity["type"] for entity in extract_proper_names(TEXT)}

    assert names["Gabriel García Márquez"] == "ENTITY"
    assert names["Universidad Nacional de Colombia"] == "ORGANIZATION"
    assert "Bogotá" in names
    # A verb that only opens a sentence is not a name.
    assert "Trabajó" not in names
    assert "La" not in names


def test_links_names_mentioned_in_the_same_sentence() -> None:
    names = extract_proper_names(TEXT)
    relations = extract_name_relations(TEXT, names)

    assert {
        "source": "Gabriel García Márquez",
        "relation": "MENTIONED_WITH",
        "target": "Aracataca",
    } in relations
    assert all(relation["source"] != relation["target"] for relation in relations)


def test_rules_analysis_includes_names_and_no_duplicate_years() -> None:
    result = analyze_text_with_rules(TEXT)
    values = [(entity["value"], entity["type"]) for entity in result["entities"]]

    assert ("Colombia", "ENTITY") in values
    assert ("1927", "YEAR") in values
    assert ("1927", "NUMBER") not in values
    assert any(r["relation"] == "MENTIONED_WITH" for r in result["relations"])


def test_names_joined_by_y_are_separate() -> None:
    names = [e["value"] for e in extract_proper_names("Viajó entre Bogotá y Barranquilla.")]
    assert names == ["Bogotá", "Barranquilla"]
