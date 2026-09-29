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


def find_metric_number_relations(
    entities: list[dict]
) -> list[dict]:

    metrics = [
        entity
        for entity in entities
        if entity["type"] == "METRIC"
    ]

    numbers = [
        entity
        for entity in entities
        if entity["type"] == "NUMBER"
    ]

    relations = []

    for metric in metrics:

        for number in numbers:

            relations.append({
                "source": metric["value"],
                "relation": "HAS_VALUE",
                "target": number["value"]
            })

    return relations


def find_column_type_relations(
    entities: list[dict]
) -> list[dict]:

    columns = [
        entity
        for entity in entities
        if entity["type"] in [
            "NUMERIC_COLUMN",
            "CATEGORICAL_COLUMN",
            "DATE_COLUMN"
        ]
    ]

    relations = []

    for column in columns:

        if column["type"] == "NUMERIC_COLUMN":

            relations.append({
                "source": column["value"],
                "relation": "HAS_TYPE",
                "target": "NUMERIC"
            })

        elif column["type"] == "CATEGORICAL_COLUMN":

            relations.append({
                "source": column["value"],
                "relation": "HAS_TYPE",
                "target": "CATEGORICAL"
            })

        elif column["type"] == "DATE_COLUMN":

            relations.append({
                "source": column["value"],
                "relation": "HAS_TYPE",
                "target": "DATE"
            })

    return relations


def find_column_relationships(
    entities: list[dict]
) -> list[dict]:

    numeric_columns = [
        entity
        for entity in entities
        if entity["type"] == "NUMERIC_COLUMN"
    ]

    categorical_columns = [
        entity
        for entity in entities
        if entity["type"] == "CATEGORICAL_COLUMN"
    ]

    date_columns = [
        entity
        for entity in entities
        if entity["type"] == "DATE_COLUMN"
    ]

    relations = []

    for categorical in categorical_columns:

        for numeric in numeric_columns:

            relations.append({
                "source": categorical["value"],
                "relation": "CAN_BE_ANALYZED_WITH",
                "target": numeric["value"]
            })

    for date_column in date_columns:

        for numeric in numeric_columns:

            relations.append({
                "source": date_column["value"],
                "relation": "TEMPORAL_ANALYSIS_OF",
                "target": numeric["value"]
            })

    return relations


def remove_duplicate_relations(
    relations: list[dict]
) -> list[dict]:

    unique_relations = []

    seen = set()

    for relation in relations:

        key = (
            relation["source"],
            relation["relation"],
            relation["target"]
        )

        if key in seen:
            continue

        seen.add(key)

        unique_relations.append(
            relation
        )

    return unique_relations


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

    relations.extend(
        find_metric_number_relations(
            entities
        )
    )

    relations.extend(
        find_column_type_relations(
            entities
        )
    )

    relations.extend(
        find_column_relationships(
            entities
        )
    )

    return remove_duplicate_relations(
        relations
    )