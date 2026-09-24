from app.services.document_processor import process_document
from app.services.text_processor import process_text
from app.services.entity_extractor import extract_entities
from app.services.relation_extractor import extract_relations


# ==========================================
# ARCHIVO
# ==========================================

file_path = "uploads/a10d79f1-6f07-4830-acc9-72f6d2eee465.pdf"


# ==========================================
# EXTRAER TEXTO
# ==========================================

text = process_document(
    file_path
)


# ==========================================
# PROCESAR TEXTO
# ==========================================

result = process_text(
    text
)


# ==========================================
# EXTRAER ENTIDADES
# ==========================================

entities = extract_entities(
    result["normalized_text"]
)


# ==========================================
# EXTRAER RELACIONES
# ==========================================

relations = extract_relations(
    entities
)


# ==========================================
# MOSTRAR ENTIDADES
# ==========================================

print("\n===================================")
print("ENTIDADES")
print("===================================\n")


for entity in entities:

    print(
        f"{entity['value']} "
        f"({entity['type']})"
    )


# ==========================================
# MOSTRAR RELACIONES
# ==========================================

print("\n===================================")
print("RELACIONES DETECTADAS")
print("===================================\n")


for relation in relations:

    print(
        f"{relation['source']} "
        f"--[{relation['relation']}]--> "
        f"{relation['target']}"
    )