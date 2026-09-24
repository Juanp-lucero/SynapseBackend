import re


# ==========================================
# DETECTAR PATRÓN DE CATEGORÍAS
# ==========================================

def detect_category_pattern(
    text: str
) -> list[dict]:

    patterns = []

    text_lower = text.lower()

    categories = [
        "electronics",
        "clothing",
        "beauty"
    ]

    found_categories = []

    for category in categories:

        if category in text_lower:

            found_categories.append(
                category
            )

    if len(found_categories) >= 2:

        patterns.append({
            "type": "CATEGORY_GROUP",
            "description": (
                "El documento contiene "
                "múltiples categorías de productos."
            ),
            "entities": found_categories
        })

    return patterns


# ==========================================
# DETECTAR PATRÓN TEMPORAL
# ==========================================

def detect_temporal_pattern(
    text: str
) -> list[dict]:

    patterns = []

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    years = sorted(
        list(set(years))
    )

    if len(years) >= 2:

        patterns.append({
            "type": "TEMPORAL_COMPARISON",
            "description": (
                "El documento contiene información "
                "correspondiente a múltiples años."
            ),
            "entities": years
        })

    return patterns


# ==========================================
# DETECTAR MÉTRICAS
# ==========================================

def detect_metric_pattern(
    text: str
) -> list[dict]:

    patterns = []

    text_lower = text.lower()

    metrics = []

    possible_metrics = [
        "total ventas",
        "crecimiento interanual",
        "ticket promedio",
        "ventas",
        "crecimiento"
    ]

    for metric in possible_metrics:

        if metric in text_lower:

            metrics.append(
                metric
            )

    if len(metrics) >= 2:

        patterns.append({
            "type": "MULTIPLE_METRICS",
            "description": (
                "El documento contiene "
                "múltiples indicadores de negocio."
            ),
            "entities": metrics
        })

    return patterns


# ==========================================
# DETECTAR TODOS LOS PATRONES
# ==========================================

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

    return patterns