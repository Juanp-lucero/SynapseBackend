# ==========================================
# EXTRACTOR DE RELACIONES
# ==========================================


# ==========================================
# RELACIONES ENTRE CATEGORÍAS Y MÉTRICAS
# ==========================================

def find_category_metric_relations(
    entities: list[dict]
) -> list[dict]:

    categories = [
        entity
        for entity in entities
        if entity["type"] == "CATEGORY"
    ]

    metrics = [
        entity
        for entity in entities
        if entity["type"] == "METRIC"
    ]

    relations = []

    for category in categories:

        for metric in metrics:

            relations.append({
                "source": category["value"],
                "relation": "RELATED_TO",
                "target": metric["value"]
            })

    return relations


# ==========================================
# RELACIONES ENTRE AÑOS Y MÉTRICAS
# ==========================================

def find_year_metric_relations(
    entities: list[dict]
) -> list[dict]:

    years = [
        entity
        for entity in entities
        if entity["type"] == "YEAR"
    ]

    metrics = [
        entity
        for entity in entities
        if entity["type"] == "METRIC"
    ]

    relations = []

    for year in years:

        for metric in metrics:

            relations.append({
                "source": year["value"],
                "relation": "HAS_DATA",
                "target": metric["value"]
            })

    return relations


# ==========================================
# CONSTRUIR TODAS LAS RELACIONES
# ==========================================

def extract_relations(
    entities: list[dict]
) -> list[dict]:

    relations = []

    relations.extend(
        find_category_metric_relations(
            entities
        )
    )

    relations.extend(
        find_year_metric_relations(
            entities
        )
    )

    return relations