"""Rule-based detection of proper names (people, places, organizations).

It is intentionally simple: sequences of capitalized words, with short
connectors such as "de" or "del" allowed between them. It gives the graph
real entities even when the AI extractor is not available.
"""

import re
from itertools import combinations

UPPER = "A-ZÁÉÍÓÚÑÜ"
LOWER = "a-záéíóúñü"

_WORD = rf"[{UPPER}][{LOWER}]+(?:-[{UPPER}][{LOWER}]+)?"
_CONNECTOR = r"(?:de|del|de la|de los|de las|y|of|the)"
NAME_RE = re.compile(rf"\b{_WORD}(?:\s+(?:{_CONNECTOR}\s+)?{_WORD})*\b")

SENTENCE_RE = re.compile(r"[^.!?\n]+")

# Capitalized words that are usually just the start of a sentence.
STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "en", "de", "del",
    "por", "para", "con", "sin", "sobre", "entre", "este", "esta", "estos",
    "estas", "ese", "esa", "eso", "esto", "aquel", "aquella", "se", "su",
    "sus", "al", "lo", "le", "les", "y", "o", "pero", "si", "no", "como",
    "cuando", "donde", "que", "también", "además", "sin embargo", "durante",
    "según", "hay", "fue", "es", "son", "era", "the", "a", "an", "in", "on",
    "of", "for", "with", "this", "that", "these", "those", "it", "and", "or",
    "but", "if", "when", "where", "is", "are", "was", "were", "nota", "tabla",
    "figura", "capítulo", "página", "resumen", "introducción", "conclusión",
}

ORGANIZATION_WORDS = {
    "universidad", "university", "ministerio", "empresa", "compañía",
    "company", "banco", "bank", "instituto", "institute", "fundación",
    "foundation", "corporación", "corporation", "gobierno", "government",
    "agencia", "agency", "organización", "organization", "asociación",
    "colegio", "hospital", "secretaría", "alcaldía", "departamento",
    "inc", "corp", "ltda", "sas", "s.a.",
}

MAX_NAMES = 40
MAX_NAME_RELATIONS = 80


def _clean(name: str) -> str:
    words = name.split()
    while words and words[0].lower() in STOPWORDS:
        words.pop(0)
    while words and words[-1].lower() in STOPWORDS:
        words.pop()
    return " ".join(words)


def _classify(name: str) -> str:
    words = {word.lower().strip(".,") for word in name.split()}
    if words & ORGANIZATION_WORDS:
        return "ORGANIZATION"
    return "ENTITY"


def _find_with_position(sentence: str) -> list[tuple[str, bool]]:
    """Names in a sentence, flagged when they are a lone first word."""
    offset = len(sentence) - len(sentence.lstrip())
    found = []
    for match in NAME_RE.finditer(sentence):
        name = _clean(match.group(0))
        if len(name) < 3 or name.lower() in STOPWORDS:
            continue
        lone_initial = match.start() == offset and " " not in name
        found.append((name, lone_initial))
    return found


def find_names(sentence: str) -> list[str]:
    return list(dict.fromkeys(name for name, _ in _find_with_position(sentence)))


def extract_proper_names(text: str) -> list[dict]:
    """Proper names found in the text, in order of appearance.

    A single capitalized word that opens a sentence ("Trabajó ...") is only
    kept when the same word is also capitalized in the middle of a sentence.
    """
    order: dict[str, str] = {}
    confirmed: set[str] = set()
    for sentence in SENTENCE_RE.findall(text):
        for name, lone_initial in _find_with_position(sentence):
            key = name.lower()
            order.setdefault(key, name)
            if not lone_initial:
                confirmed.add(key)

    names = [
        {"value": name, "type": _classify(name)}
        for key, name in order.items()
        if key in confirmed
    ]
    return names[:MAX_NAMES]


def extract_name_relations(text: str, names: list[dict]) -> list[dict]:
    """Link names that appear together in the same sentence."""
    allowed = {entity["value"].lower(): entity["value"] for entity in names}
    relations: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for sentence in SENTENCE_RE.findall(text):
        present = [
            allowed[name.lower()]
            for name in find_names(sentence)
            if name.lower() in allowed
        ]
        for source, target in combinations(dict.fromkeys(present), 2):
            key = (source.lower(), target.lower())
            if key in seen:
                continue
            seen.add(key)
            relations.append(
                {"source": source, "relation": "MENTIONED_WITH", "target": target}
            )
            if len(relations) >= MAX_NAME_RELATIONS:
                return relations
    return relations
