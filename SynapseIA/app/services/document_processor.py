import os

from pypdf import PdfReader
from docx import Document


# ==========================================
# EXTRAER TEXTO DE PDF
# ==========================================

def extract_pdf_text(file_path: str) -> str:

    reader = PdfReader(file_path)

    text = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


# ==========================================
# EXTRAER TEXTO DE DOCX
# ==========================================

def extract_docx_text(file_path: str) -> str:

    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


# ==========================================
# EXTRAER TEXTO DE TXT
# ==========================================

def extract_txt_text(file_path: str) -> str:

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()


# ==========================================
# EXTRAER CONTENIDO DE CSV
# ==========================================

def extract_csv_text(file_path: str) -> str:

    # Pandas solamente se carga cuando realmente
    # estamos procesando un archivo CSV.

    import pandas as pd

    dataframe = pd.read_csv(file_path)

    return dataframe.to_string(index=False)


# ==========================================
# PROCESADOR PRINCIPAL
# ==========================================

def process_document(file_path: str) -> str:

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":

        return extract_pdf_text(file_path)

    elif extension == ".docx":

        return extract_docx_text(file_path)

    elif extension == ".txt":

        return extract_txt_text(file_path)

    elif extension == ".csv":

        return extract_csv_text(file_path)

    else:

        raise ValueError(
            "Tipo de archivo no soportado"
        )