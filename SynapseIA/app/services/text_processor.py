import re


# ==========================================
# LIMPIAR TEXTO
# ==========================================

def clean_text(text: str) -> str:

    if not text:
        return ""

    # Reemplazar saltos de línea repetidos
    text = re.sub(
        r"\n+",
        "\n",
        text
    )

    # Reemplazar espacios repetidos
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Eliminar espacios al inicio y final
    text = text.strip()

    return text


# ==========================================
# NORMALIZAR TEXTO
# ==========================================

def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = clean_text(text)

    # Normalizar saltos de línea
    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


# ==========================================
# DIVIDIR TEXTO EN SEGMENTOS
# ==========================================

def split_text(
    text: str,
    max_length: int = 1000
) -> list[str]:

    if not text:
        return []

    text = normalize_text(text)

    paragraphs = text.split("\n")

    segments = []

    current_segment = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # Si agregar el párrafo no supera
        # el tamaño máximo
        if len(current_segment) + len(paragraph) + 1 <= max_length:

            if current_segment:

                current_segment += "\n"

            current_segment += paragraph

        else:

            if current_segment:

                segments.append(
                    current_segment
                )

            current_segment = paragraph

    # Agregar último segmento

    if current_segment:

        segments.append(
            current_segment
        )

    return segments


# ==========================================
# PROCESAR TEXTO COMPLETO
# ==========================================

def process_text(text: str) -> dict:

    cleaned_text = clean_text(
        text
    )

    normalized_text = normalize_text(
        cleaned_text
    )

    segments = split_text(
        normalized_text
    )

    return {
    "original_length": len(text),
    "cleaned_length": len(cleaned_text),
    "normalized_length": len(normalized_text),
    "normalized_text": normalized_text,
    "segments_count": len(segments),
    "segments": segments
}