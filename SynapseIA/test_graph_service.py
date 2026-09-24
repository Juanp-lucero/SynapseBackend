from app.services.graph_service import save_entities_and_relations


entities = [
    {
        "value": "Electronics",
        "type": "CATEGORY"
    },
    {
        "value": "Total Ventas",
        "type": "METRIC"
    }
]


relations = [
    {
        "source": "Electronics",
        "relation": "RELATED_TO",
        "target": "Total Ventas"
    }
]


save_entities_and_relations(
    source_id=999,
    source_name="Prueba Synapse IA",
    entities=entities,
    relations=relations
)

print("Grafo guardado correctamente en Neo4j")