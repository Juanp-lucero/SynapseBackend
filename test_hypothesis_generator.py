from app.services.document_processor import process_document
from app.services.text_processor import process_text
from app.services.entity_extractor import extract_entities
from app.services.relation_extractor import extract_relations
from app.services.pattern_detector import detect_patterns
from app.services.hypothesis_generator import generate_hypotheses


# ==========================================
# ARCHIVO
# ==========================================

file_path = "uploads/a10d79f1-6f07-4830-acc9-72f6d2eee465.pdf"


# ==========================================
# EXTRAER
# ==========================================

text = process_document(
    file_path
)


# ==========================================
# PROCESAR
# ==========================================

result = process_text(
    text
)


normalized_text = result[
    "normalized_text"
]


# ==========================================
# ENTIDADES
# ==========================================

entities = extract_entities(
    normalized_text
)


# ==========================================
# RELACIONES
# ==========================================

relations = extract_relations(
    entities
)


# ==========================================
# PATRONES
# ==========================================

patterns = detect_patterns(
    normalized_text
)


# ==========================================
# HIPÓTESIS
# ==========================================

hypotheses = generate_hypotheses(
    entities,
    relations,
    patterns
)


# ==========================================
# MOSTRAR
# ==========================================

print("\n===================================")
print("HIPÓTESIS GENERADAS")
print("===================================\n")


for index, hypothesis in enumerate(
    hypotheses,
    start=1
):

    print(
        f"\nHIPÓTESIS {index}"
    )

    print(
        f"Título: "
        f"{hypothesis['title']}"
    )

    print(
        f"Descripción: "
        f"{hypothesis['description']}"
    )

    print(
        "Evidencia:"
    )

    for evidence in hypothesis[
        "evidence"
    ]:

        print(
            f"  - {evidence}"
        )

    print(
        f"Confianza: "
        f"{hypothesis['confidence']}"
    )

    print(
        "-----------------------------------"
    )