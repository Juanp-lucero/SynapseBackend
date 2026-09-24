from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.database.neo4j_connection import driver, NEO4J_DATABASE
from app.models.user import User


router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"]
)


@router.get("/source/{source_id}")
def get_source_graph(
    source_id: int,
    current_user: User = Depends(get_current_user)
):

    try:

        with driver.session(
            database=NEO4J_DATABASE
        ) as session:

            result = session.run(
                """
                MATCH (d:Document {
                    source_id: $source_id
                })

                OPTIONAL MATCH (n)-[r]->(m)

                WHERE
                    (n = d OR m = d)
                    OR
                    (n:Entity AND m:Entity)

                RETURN
                    labels(n) AS source_labels,
                    properties(n) AS source,
                    type(r) AS relation,
                    labels(m) AS target_labels,
                    properties(m) AS target
                """,
                source_id=source_id
            )

            nodes = {}
            relationships = []

            for record in result:

                source = record["source"]
                target = record["target"]

                source_key = str(source)

                if source_key not in nodes:

                    nodes[source_key] = {
                        "labels": record["source_labels"],
                        "properties": source
                    }

                if target:

                    target_key = str(target)

                    if target_key not in nodes:

                        nodes[target_key] = {
                            "labels": record["target_labels"],
                            "properties": target
                        }

                    relationships.append({
                        "source": source,
                        "relation": record["relation"],
                        "target": target
                    })

            return {
                "source_id": source_id,
                "nodes": list(nodes.values()),
                "relationships": relationships
            }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error consultando el grafo: {str(e)}"
        )