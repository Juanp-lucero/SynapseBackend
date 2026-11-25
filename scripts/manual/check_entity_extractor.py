from app.services.document_processor import process_document
from app.services.text_processor import process_text
from app.services.entity_extractor import extract_entities


# ==========================================
# Archivo
# ==========================================

file_path = "uploads/a10d79f1-6f07-4830-acc9-72f6d2eee465.pdf"


# ==========================================
# Extraer texto
# ==========================================

text = process_document(
    file_path
)


# ==========================================
# Procesar texto
# ==========================================

result = process_text(
    text
)


# ==========================================
# Extraer entidades
# ==========================================

entities = extract_entities(
    result["normalized_text"]
    if "normalized_text" in result
    else text
)


# ==========================================
# Mostrar entidades
# ==========================================

print("\n===================================")
print("ENTIDADES DETECTADAS")
print("===================================\n")


for entity in entities:

    print(
        f"Valor: {entity['value']}"
    )

    print(
        f"Tipo: {entity['type']}"
    )

    print("-----------------------------------")