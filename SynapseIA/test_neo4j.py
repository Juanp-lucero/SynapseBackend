from app.database.neo4j_connection import verify_neo4j_connection


try:

    verify_neo4j_connection()

    print("Neo4j conectado correctamente")

except Exception as e:

    print("Error conectando con Neo4j:")
    print(e)