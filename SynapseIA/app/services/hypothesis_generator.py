def generate_relation_hypotheses(
    relations: list[dict]
) -> list[dict]:

    hypotheses = []

    for relation in relations:

        source = relation["source"]
        relation_type = relation["relation"]
        target = relation["target"]

        if relation_type == "RELATED_TO":

            hypotheses.append({
                "title": (
                    f"Posible relación entre "
                    f"{source} y {target}"
                ),
                "description": (
                    f"El documento presenta una posible "
                    f"relación entre la categoría "
                    f"{source} y el indicador {target}."
                ),
                "evidence": [
                    f"La entidad {source} fue identificada.",
                    f"La entidad {target} fue identificada.",
                    (
                        f"Se detectó la relación "
                        f"{relation_type}."
                    )
                ],
                "confidence": 0.65
            })

        elif relation_type == "HAS_DATA":

            hypotheses.append({
                "title": (
                    f"Información temporal asociada "
                    f"a {target}"
                ),
                "description": (
                    f"El documento contiene información "
                    f"del indicador {target} asociada "
                    f"al año {source}."
                ),
                "evidence": [
                    f"Se identificó el año {source}.",
                    f"Se identificó el indicador {target}.",
                    (
                        f"Se detectó la relación "
                        f"{relation_type}."
                    )
                ],
                "confidence": 0.75
            })

        elif relation_type == "HAS_VALUE":

            hypotheses.append({
                "title": (
                    f"Indicador {source} "
                    f"con valor numérico"
                ),
                "description": (
                    f"El documento presenta el indicador "
                    f"{source} acompañado de un valor "
                    f"numérico identificado como {target}."
                ),
                "evidence": [
                    f"Se identificó el indicador {source}.",
                    f"Se identificó el valor {target}.",
                    (
                        f"Se detectó la relación "
                        f"{relation_type}."
                    )
                ],
                "confidence": 0.70
            })

    return hypotheses


def generate_pattern_hypotheses(
    patterns: list[dict]
) -> list[dict]:

    hypotheses = []

    for pattern in patterns:

        pattern_type = pattern["type"]
        entities = pattern["entities"]

        if pattern_type == "CATEGORY_GROUP":

            hypotheses.append({
                "title": "Diversidad de categorías",
                "description": (
                    "El documento presenta información "
                    "distribuida entre múltiples categorías."
                ),
                "evidence": [
                    (
                        f"Se identificaron las categorías: "
                        f"{', '.join(entities)}."
                    )
                ],
                "confidence": 0.80
            })

        elif pattern_type == "TEMPORAL_COMPARISON":

            hypotheses.append({
                "title": "Comparación temporal posible",
                "description": (
                    "La información contiene datos "
                    "correspondientes a diferentes años, "
                    "lo que permite realizar una comparación "
                    "temporal."
                ),
                "evidence": [
                    (
                        f"Se identificaron los años: "
                        f"{', '.join(entities)}."
                    )
                ],
                "confidence": 0.85
            })

        elif pattern_type == "MULTIPLE_METRICS":

            hypotheses.append({
                "title": "Múltiples indicadores identificados",
                "description": (
                    "El documento combina diferentes "
                    "indicadores que pueden utilizarse "
                    "para analizar el comportamiento "
                    "de la información."
                ),
                "evidence": [
                    (
                        f"Se identificaron los indicadores: "
                        f"{', '.join(entities)}."
                    )
                ],
                "confidence": 0.80
            })

        elif pattern_type == "METRIC_WITH_VALUES":

            hypotheses.append({
                "title": "Indicadores acompañados de valores",
                "description": (
                    "El documento presenta indicadores "
                    "acompañados de valores numéricos, "
                    "lo que puede permitir un análisis "
                    "cuantitativo."
                ),
                "evidence": [
                    (
                        f"Elementos identificados: "
                        f"{', '.join(entities)}."
                    )
                ],
                "confidence": 0.75
            })

    return hypotheses


def remove_duplicate_hypotheses(
    hypotheses: list[dict]
) -> list[dict]:

    unique_hypotheses = []

    seen = set()

    for hypothesis in hypotheses:

        key = (
            hypothesis["title"],
            hypothesis["description"]
        )

        if key in seen:
            continue

        seen.add(key)

        unique_hypotheses.append(
            hypothesis
        )

    return unique_hypotheses


def generate_hypotheses(
    entities: list[dict],
    relations: list[dict],
    patterns: list[dict]
) -> list[dict]:

    hypotheses = []

    relation_hypotheses = (
        generate_relation_hypotheses(
            relations
        )
    )

    pattern_hypotheses = (
        generate_pattern_hypotheses(
            patterns
        )
    )

    hypotheses.extend(
        relation_hypotheses
    )

    hypotheses.extend(
        pattern_hypotheses
    )

    return remove_duplicate_hypotheses(
        hypotheses
    )