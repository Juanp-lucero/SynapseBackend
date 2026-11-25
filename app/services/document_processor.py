import os

from pypdf import PdfReader
from docx import Document


def extract_pdf_text(file_path: str) -> str:

    reader = PdfReader(file_path)

    text = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_docx_text(file_path: str) -> str:

    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


def extract_txt_text(file_path: str) -> str:

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()


def extract_csv_text(file_path: str) -> str:

    import pandas as pd

    dataframe = pd.read_csv(file_path)

    lines = []

    columns = dataframe.columns.tolist()

    lines.append(
        "TIPO DE FUENTE: DATASET CSV"
    )

    lines.append(
        f"NUMERO DE FILAS: {len(dataframe)}"
    )

    lines.append(
        f"NUMERO DE COLUMNAS: {len(columns)}"
    )

    lines.append(
        "COLUMNAS: " + ", ".join(
            str(column)
            for column in columns
        )
    )

    lines.append(
        "TIPOS DE DATOS:"
    )

    for column in columns:

        lines.append(
            f"{column}: {dataframe[column].dtype}"
        )

    lines.append(
        "DATOS DEL DATASET:"
    )

    lines.append(
        dataframe.to_string(
            index=False
        )
    )

    return "\n".join(lines)


def process_document(file_path: str) -> str:

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":

        return extract_pdf_text(
            file_path
        )

    elif extension == ".docx":

        return extract_docx_text(
            file_path
        )

    elif extension == ".txt":

        return extract_txt_text(
            file_path
        )

    elif extension == ".csv":

        return extract_csv_text(
            file_path
        )

    else:

        raise ValueError(
            "Tipo de archivo no soportado"
        )