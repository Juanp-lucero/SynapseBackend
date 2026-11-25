from neo4j import GraphDatabase

from app.core.config import settings


driver = None
NEO4J_DATABASE = settings.neo4j_database or "neo4j"

if settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password:
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(
            settings.neo4j_username,
            settings.neo4j_password
        )
    )


def is_neo4j_configured() -> bool:
    return driver is not None


def get_neo4j_driver():
    if driver is None:
        raise RuntimeError(
            "Neo4j no está configurado. Revisa NEO4J_URI, "
            "NEO4J_USERNAME y NEO4J_PASSWORD."
        )
    return driver


def verify_neo4j_connection():
    neo4j_driver = get_neo4j_driver()
    neo4j_driver.verify_connectivity()
    return True
