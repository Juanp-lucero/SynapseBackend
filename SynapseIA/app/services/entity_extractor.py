import re


# ==========================================
# PALABRAS QUE PUEDEN REPRESENTAR CATEGORÍAS
# ==========================================

CATEGORY_KEYWORDS = {
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
    "employees"
}


# ==========================================
# EXTRAER AÑOS
# ==========================================

def extract_years(text: str) -> list[str]:

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    return sorted(
        list(set(years))
    )


# ==========================================
# EXTRAER CANTIDADES
# ==========================================

def extract_numbers(text: str) -> list[str]:

    numbers = re.findall(
        r"\b\d+(?:[.,]\d+)?\b",
        text
    )

    return list(
        dict.fromkeys(numbers)
    )


# ==========================================
# EXTRAER CATEGORÍAS
# ==========================================

def extract_categories(text: str) -> list[str]:

    text_lower = text.lower()

    categories = []

    for keyword in CATEGORY_KEYWORDS:

        if keyword in text_lower:

            categories.append(
                keyword
            )

    return categories


# ==========================================
# EXTRAER INDICADORES
# ==========================================

def extract_metrics(text: str) -> list[str]:

    metrics = []

    metric_patterns = [
        r"total ventas",
        r"crecimiento interanual",
        r"ticket promedio",
        r"ventas",
        r"crecimiento",
        r"ingresos",
        r"precio"
    ]

    text_lower = text.lower()

    for pattern in metric_patterns:

        if re.search(
            pattern,
            text_lower
        ):

            metrics.append(
                pattern
            )

    return list(
        dict.fromkeys(metrics)
    )


# ==========================================
# EXTRAER ENTIDADES
# ==========================================

def extract_entities(text: str) -> list[dict]:

    entities = []

    # Años

    for year in extract_years(text):

        entities.append({
            "value": year,
            "type": "YEAR"
        })


    # Números

    for number in extract_numbers(text):

        entities.append({
            "value": number,
            "type": "NUMBER"
        })


    # Categorías

    for category in extract_categories(text):

        entities.append({
            "value": category,
            "type": "CATEGORY"
        })


    # Métricas

    for metric in extract_metrics(text):

        entities.append({
            "value": metric,
            "type": "METRIC"
        })


    return entities