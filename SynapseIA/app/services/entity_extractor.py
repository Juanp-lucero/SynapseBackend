import re


CATEGORY_KEYWORDS = {
    "electronics": "electronics",
    "clothing": "clothing",
    "beauty": "beauty",
    "technology": "technology",
    "health": "health",
    "finance": "finance",
    "education": "education",
    "sales": "sales",
    "marketing": "marketing",
    "products": "products",
    "customers": "customers",
    "employees": "employees",
    "tecnologia": "technology",
    "tecnología": "technology",
    "salud": "health",
    "finanzas": "finance",
    "educacion": "education",
    "educación": "education",
    "ventas": "sales",
    "mercadeo": "marketing",
    "productos": "products",
    "clientes": "customers",
    "empleados": "employees"
}


METRIC_KEYWORDS = [
    "total ventas",
    "crecimiento interanual",
    "ticket promedio",
    "ventas",
    "crecimiento",
    "ingresos",
    "precio",
    "rentabilidad",
    "ganancia",
    "costos",
    "coste",
    "margen"
]


DATE_COLUMN_NAMES = {
    "date",
    "fecha",
    "datetime",
    "fecha_registro",
    "fecha_creacion",
    "fecha_actualizacion",
    "timestamp",
    "time"
}


def extract_years(text: str) -> list[str]:

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    return sorted(
        list(set(years))
    )


def extract_numbers(text: str) -> list[str]:

    numbers = re.findall(
        r"\b\d+(?:[.,]\d+)?\b",
        text
    )

    return list(
        dict.fromkeys(numbers)
    )


def extract_categories(text: str) -> list[str]:

    text_lower = text.lower()

    categories = []

    for keyword, normalized_value in CATEGORY_KEYWORDS.items():

        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(
            pattern,
            text_lower
        ):
            categories.append(
                normalized_value
            )

    return list(
        dict.fromkeys(categories)
    )


def extract_metrics(text: str) -> list[str]:

    text_lower = text.lower()

    metrics = []

    for metric in METRIC_KEYWORDS:

        pattern = rf"\b{re.escape(metric)}\b"

        if re.search(
            pattern,
            text_lower
        ):
            metrics.append(
                metric
            )

    return list(
        dict.fromkeys(metrics)
    )


def extract_csv_columns(text: str) -> list[dict]:

    columns_match = re.search(
        r"^COLUMNAS:\s*(.+)$",
        text,
        re.IGNORECASE | re.MULTILINE
    )

    if not columns_match:
        return []

    columns_text = columns_match.group(1)

    columns = [
        column.strip()
        for column in columns_text.split(",")
        if column.strip()
    ]

    return [
        {
            "value": column,
            "type": "COLUMN"
        }
        for column in columns
    ]


def extract_csv_column_types(
    text: str
) -> list[dict]:

    types_match = re.search(
        r"^TIPOS DE DATOS:\s*(.*?)^DATOS DEL DATASET:",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    if not types_match:
        return []

    types_text = types_match.group(1)

    entities = []

    for line in types_text.splitlines():

        line = line.strip()

        if not line or ":" not in line:
            continue

        column, data_type = line.split(
            ":",
            1
        )

        column = column.strip()
        data_type = data_type.strip().lower()

        if not column:
            continue

        normalized_column = column.lower()

        if normalized_column in DATE_COLUMN_NAMES:

            entity_type = "DATE_COLUMN"

        elif any(
            numeric_type in data_type
            for numeric_type in [
                "int",
                "float",
                "double",
                "decimal",
                "number",
                "numeric"
            ]
        ):

            entity_type = "NUMERIC_COLUMN"

        elif any(
            date_type in data_type
            for date_type in [
                "date",
                "datetime",
                "time"
            ]
        ):

            entity_type = "DATE_COLUMN"

        else:

            entity_type = "CATEGORICAL_COLUMN"

        entities.append({
            "value": column,
            "type": entity_type,
            "data_type": data_type
        })

    return entities


def extract_entities(text: str) -> list[dict]:

    entities = []

    for year in extract_years(text):

        entities.append({
            "value": year,
            "type": "YEAR"
        })

    for number in extract_numbers(text):

        entities.append({
            "value": number,
            "type": "NUMBER"
        })

    for category in extract_categories(text):

        entities.append({
            "value": category,
            "type": "CATEGORY"
        })

    for metric in extract_metrics(text):

        entities.append({
            "value": metric,
            "type": "METRIC"
        })

    csv_columns = extract_csv_columns(
        text
    )

    csv_column_types = extract_csv_column_types(
        text
    )

    typed_columns = {
        entity["value"].lower(): entity
        for entity in csv_column_types
    }

    for column in csv_columns:

        column_name = column["value"]

        typed_column = typed_columns.get(
            column_name.lower()
        )

        if typed_column:

            entities.append(
                typed_column
            )

        else:

            entities.append({
                "value": column_name,
                "type": "COLUMN"
            })

    existing_keys = set()

    unique_entities = []

    for entity in entities:

        key = (
            entity["value"],
            entity["type"]
        )

        if key in existing_keys:
            continue

        existing_keys.add(key)

        unique_entities.append(
            entity
        )

    return unique_entities