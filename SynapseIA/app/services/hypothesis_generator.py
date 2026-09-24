# ==========================================
# GENERADOR DE HIPÓTESIS
# ==========================================


def generate_hypotheses(
    entities: list[dict],
    relations: list[dict],
    patterns: list[dict]
) -> list[dict]:

    hypotheses = []


    # ==========================================
    # HIPÓTESIS BASADAS EN RELACIONES
    # ==========================================

    for relation in relations:

        source = relation["source"]
        relation_type = relation["relation"]
        target = relation["target"]


        hypothesis = {
            "title": (
                f"Relación entre "
                f"{source} y {target}"
            ),

            "description": (
                f"Los datos analizados presentan "
                f"una relación {relation_type} "
                f"entre {source} y {target}."
            ),

            "evidence": [
                f"La entidad {source} "
                f"fue identificada.",

                f"La entidad {target} "
                f"fue identificada.",

                (
                    f"Se detectó la relación "
                    f"{relation_type}."
                )
            ],

            "confidence": 0.70
        }


        hypotheses.append(
            hypothesis
        )


    # ==========================================
    # HIPÓTESIS BASADAS EN PATRONES
    # ==========================================

    for pattern in patterns:

        if pattern["type"] == "CATEGORY_GROUP":

            hypotheses.append({

                "title":
                    "Diversidad de categorías",

                "description":
                    (
                        "El documento presenta "
                        "información distribuida "
                        "entre diferentes "
                        "categorías de productos."
                    ),

                "evidence":
                    pattern["entities"],

                "confidence":
                    0.80
            })


        elif pattern["type"] == "TEMPORAL_COMPARISON":

            hypotheses.append({

                "title":
                    "Comparación temporal",

                "description":
                    (
                        "Los datos permiten realizar "
                        "una comparación entre "
                        "diferentes períodos."
                    ),

                "evidence":
                    pattern["entities"],

                "confidence":
                    0.85
            })


        elif pattern["type"] == "MULTIPLE_METRICS":

            hypotheses.append({

                "title":
                    "Múltiples indicadores",

                "description":
                    (
                        "El documento combina "
                        "diferentes indicadores "
                        "para representar "
                        "el comportamiento del negocio."
                    ),

                "evidence":
                    pattern["entities"],

                "confidence":
                    0.80
            })


    return hypotheses