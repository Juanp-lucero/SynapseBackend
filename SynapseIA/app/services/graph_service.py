from app.database.neo4j_connection import driver, NEO4J_DATABASE


def save_analysis_to_graph(
    source_id: int,
    source_name: str,
    entities: list[dict],
    relations: list[dict],
    patterns: list[dict],
    hypotheses: list[dict]
):

    with driver.session(
        database=NEO4J_DATABASE
    ) as session:

        session.run(
            """
            MERGE (d:Document {
                source_id: $source_id
            })
            SET d.name = $source_name
            """,
            source_id=source_id,
            source_name=source_name
        )

        for entity in entities:

            session.run(
                """
                MERGE (e:Entity {
                    name: $name,
                    type: $type
                })

                WITH e

                MATCH (d:Document {
                    source_id: $source_id
                })

                MERGE (e)-[:MENTIONED_IN]->(d)
                """,
                name=entity["value"],
                type=entity["type"],
                source_id=source_id
            )

        for relation in relations:

            session.run(
                """
                MERGE (source:Entity {
                    name: $source_name
                })

                MERGE (target:Entity {
                    name: $target_name
                })

                MERGE (source)-[r:RELATED_TO]->(target)

                SET r.relation_type = $relation_type
                """,
                source_name=relation["source"],
                target_name=relation["target"],
                relation_type=relation["relation"]
            )

        for pattern in patterns:

            pattern_type = pattern.get(
                "type",
                "UNKNOWN"
            )

            description = pattern.get(
                "description",
                ""
            )

            session.run(
                """
                MERGE (p:Pattern {
                    type: $type,
                    description: $description
                })

                WITH p

                MATCH (d:Document {
                    source_id: $source_id
                })

                MERGE (p)-[:DETECTED_IN]->(d)
                """,
                type=pattern_type,
                description=description,
                source_id=source_id
            )

        for hypothesis in hypotheses:

            title = hypothesis.get(
                "title",
                "Sin título"
            )

            description = hypothesis.get(
                "description",
                ""
            )

            confidence = hypothesis.get(
                "confidence",
                0
            )

            session.run(
                """
                MERGE (h:Hypothesis {
                    title: $title,
                    source_id: $source_id
                })

                SET h.description = $description,
                    h.confidence = $confidence

                WITH h

                MATCH (d:Document {
                    source_id: $source_id
                })

                MERGE (h)-[:GENERATED_FROM]->(d)
                """,
                title=title,
                source_id=source_id,
                description=description,
                confidence=confidence
            )