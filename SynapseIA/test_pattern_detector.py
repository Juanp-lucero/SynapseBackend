from app.services.document_processor import process_document
from app.services.text_processor import process_text
from app.services.pattern_detector import detect_patterns


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
# DETECTAR PATRONES
# ==========================================

patterns = detect_patterns(
    result["normalized_text"]
)


# ==========================================
# MOSTRAR RESULTADOS
# ==========================================

print("\n===================================")
print("PATRONES DETECTADOS")
print("===================================\n")


for index, pattern in enumerate(
    patterns,
    start=1
):

    print(
        f"Patrón {index}"
    )

    print(
        f"Tipo: {pattern['type']}"
    )

    print(
        f"Descripción: "
        f"{pattern['description']}"
    )

    print(
        f"Entidades: "
        f"{', '.join(pattern['entities'])}"
    )

    print(
        "-----------------------------------"
    )