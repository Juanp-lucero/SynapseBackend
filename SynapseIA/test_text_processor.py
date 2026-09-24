from app.services.document_processor import process_document
from app.services.text_processor import process_text


# ==========================================
# Archivo de prueba
# ==========================================

file_path = "uploads/a10d79f1-6f07-4830-acc9-72f6d2eee465.pdf"


# ==========================================
# Extraer texto
# ==========================================

text = process_document(
    file_path
)


print("\n===================================")
print("EXTRACCIÓN")
print("===================================\n")

print(
    f"Caracteres extraídos: {len(text)}"
)


# ==========================================
# Procesar texto
# ==========================================

result = process_text(
    text
)


print("\n===================================")
print("PROCESAMIENTO")
print("===================================\n")

print(
    f"Longitud original: "
    f"{result['original_length']}"
)

print(
    f"Longitud después de limpiar: "
    f"{result['cleaned_length']}"
)

print(
    f"Longitud normalizada: "
    f"{result['normalized_length']}"
)

print(
    f"Cantidad de segmentos: "
    f"{result['segments_count']}"
)


# ==========================================
# Mostrar segmentos
# ==========================================

print("\n===================================")
print("SEGMENTOS")
print("===================================\n")


for index, segment in enumerate(
    result["segments"],
    start=1
):

    print(
        f"\n--- Segmento {index} ---\n"
    )

    print(segment)