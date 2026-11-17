from neo4j import GraphDatabase

from app.core.config import settings


driver = None

if (
    settings.neo4j_uri
    and settings.neo4j_username
    and settings.neo4j_password
):
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )


def verify_neo4j_connection():
    if driver is None:
        raise RuntimeError(
            "Neo4j no está configurado. Revisa las variables NEO4J_*."
        )

    driver.verify_connectivity()
    return True
