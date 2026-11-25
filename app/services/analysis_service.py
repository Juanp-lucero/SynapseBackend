from app.services.document_processor import process_document
from app.services.text_processor import process_text
from app.services.entity_extractor import extract_entities
from app.services.relation_extractor import extract_relations
from app.services.pattern_detector import detect_patterns
from app.services.hypothesis_generator import generate_hypotheses
from app.services.ai_extractor import extract_with_ai, merge_extraction
from app.services.name_extractor import extract_name_relations, extract_proper_names


def analyze_document(file_path: str) -> dict:
    """Extract text from a supported file and analyze its contents."""
    text = process_document(file_path)
    return analyze_text(text)


def analyze_text(text: str, use_ai: bool = True) -> dict:
    """Analyze plain text with rules and, when configured, with AI.

    The deterministic pipeline always runs. When the Groq API key is
    configured, the language model adds named entities, relations and
    evidence-based hypotheses that are validated against the text.
    """
    result = analyze_text_with_rules(text)
    if not use_ai:
        return result
    return merge_extraction(result, extract_with_ai(text))


def analyze_text_with_rules(text: str) -> dict:
    """Run the existing deterministic extraction pipeline on plain text."""
    processed_text = process_text(text)
    normalized_text = processed_text["normalized_text"]

    entities = extract_entities(normalized_text)
    names = extract_proper_names(normalized_text)
    entities.extend(names)
    relations = extract_relations(entities)
    relations.extend(extract_name_relations(normalized_text, names))
    patterns = detect_patterns(normalized_text)
    hypotheses = generate_hypotheses(entities, relations, patterns)

    return {
        "entities": entities,
        "relations": relations,
        "patterns": patterns,
        "hypotheses": hypotheses,
    }
