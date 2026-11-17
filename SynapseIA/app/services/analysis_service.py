from app.services.document_processor import process_document
from app.services.text_processor import process_text
from app.services.entity_extractor import extract_entities
from app.services.relation_extractor import extract_relations
from app.services.pattern_detector import detect_patterns
from app.services.hypothesis_generator import generate_hypotheses


def analyze_document(file_path: str) -> dict:
    """Extract text from a supported file and analyze its contents."""
    text = process_document(file_path)
    return analyze_text(text)


def analyze_text(text: str) -> dict:
    """Run the existing deterministic extraction pipeline on plain text."""
    processed_text = process_text(text)
    normalized_text = processed_text["normalized_text"]

    entities = extract_entities(normalized_text)
    relations = extract_relations(entities)
    patterns = detect_patterns(normalized_text)
    hypotheses = generate_hypotheses(entities, relations, patterns)

    return {
        "entities": entities,
        "relations": relations,
        "patterns": patterns,
        "hypotheses": hypotheses,
    }
