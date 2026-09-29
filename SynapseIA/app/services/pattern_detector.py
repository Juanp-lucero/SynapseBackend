import re


CATEGORY_KEYWORDS = [
    "electronics",
    "clothing",
    "beauty",
    "technology",
    "health",
    "finance",
    "education",
    "sales",
    "marketing",
    "products",
    "customers",
    "employees",
    "tecnologia",
    "tecnología",
    "salud",
    "finanzas",
    "educacion",
    "educación",
    "ventas",
    "mercadeo",
    "productos",
    "clientes",
    "empleados"
]


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


def find_years(
    text: str
) -> list[str]:

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    return sorted(
        list(set(years))
    )


def find_categories(
    text: str
) -> list[str]:

    text_lower = text.lower()

    found_categories = []

    for category in CATEGORY_KEYWORDS:

        pattern = rf"\b{re.escape(category)}\b"

        if re.search(
            pattern,
            text_lower
        ):
            found_categories.append(
                category
            )

    return list(
        dict.fromkeys(found_categories)
    )


def find_metrics(
    text: str
) -> list[str]:

    text_lower = text.lower()

    found_metrics = []

    for metric in METRIC_KEYWORDS:

        pattern = rf"\b{re.escape(metric)}\b"

        if re.search(
            pattern,
            text_lower
        ):
            found_metrics.append(
                metric
            )

    return list(
        dict.fromkeys(found_metrics)
    )


def find_numbers(
    text: str
) -> list[str]:

    numbers = re.findall(
        r"\b\d+(?:[.,]\d+)?\b",
        text
    )

    return list(
        dict.fromkeys(numbers)
    )


def detect_category_pattern(
    text: str
) -> list[dict]:

    categories = find_categories(
        text
    )

    if len(categories) < 2:
        return []

    return [{
        "type": "CATEGORY_GROUP",
        "description": (
            "El documento contiene "
            "múltiples categorías de información."
        ),
        "entities": categories
    }]


def detect_temporal_pattern(
    text: str
) -> list[dict]:

    years = find_years(
        text
    )

    if len(years) < 2:
        return []

    return [{
        "type": "TEMPORAL_COMPARISON",
        "description": (
            "El documento contiene información "
            "correspondiente a múltiples años."
        ),
        "entities": years
    }]


def detect_metric_pattern(
    text: str
) -> list[dict]:

    metrics = find_metrics(
        text
    )

    if len(metrics) < 2:
        return []

    return [{
        "type": "MULTIPLE_METRICS",
        "description": (
            "El documento contiene "
            "múltiples indicadores de información."
        ),
        "entities": metrics
    }]


def detect_metric_value_pattern(
    text: str
) -> list[dict]:

    metrics = find_metrics(
        text
    )

    numbers = find_numbers(
        text
    )

    if not metrics or not numbers:
        return []

    return [{
        "type": "METRIC_WITH_VALUES",
        "description": (
            "El documento contiene indicadores "
            "acompañados de valores numéricos."
        ),
        "entities": metrics + numbers
    }]


def detect_patterns(
    text: str
) -> list[dict]:

    patterns = []

    patterns.extend(
        detect_category_pattern(
            text
        )
    )

    patterns.extend(
        detect_temporal_pattern(
            text
        )
    )

    patterns.extend(
        detect_metric_pattern(
            text
        )
    )

    patterns.extend(
        detect_metric_value_pattern(
            text
        )
    )

    return patterns