"""Build the Knowledge Graph from analysis results stored in PostgreSQL.

PostgreSQL is the source of truth for every analysis, so the graph can always
be generated from it, even when Neo4j is not configured. The response keeps
the same shape used by the Neo4j query (``nodes`` with ``labels`` and
``properties``, and ``relationships`` with ``source``, ``relation`` and
``target``), so the frontend does not need to know where the graph came from.
"""

from typing import Any, Iterable

# Entity types that are too generic to connect two different documents.
# Two reports that both mention "2024" or "30" are not really related.
WEAK_LINK_TYPES = {"NUMBER", "YEAR"}


def _entity_key(name: str, entity_type: str) -> tuple[str, str]:
    return (" ".join(str(name).split()).lower(), str(entity_type).upper())


class GraphAccumulator:
    """Collects unique nodes and relationships while the graph is built."""

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._relationships: dict[tuple[str, str, str], dict[str, Any]] = {}

    def add_node(
        self, key: str, label: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        if key not in self._nodes:
            self._nodes[key] = {
                "labels": [label],
                "properties": properties,
            }
        return self._nodes[key]["properties"]

    def add_relationship(
        self,
        source_key: str,
        relation: str,
        target_key: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        if source_key not in self._nodes or target_key not in self._nodes:
            return
        if source_key == target_key:
            return

        rel_key = (source_key, relation, target_key)
        if rel_key in self._relationships:
            return

        self._relationships[rel_key] = {
            "source": self._nodes[source_key]["properties"],
            "relation": relation,
            "target": self._nodes[target_key]["properties"],
            **({"properties": properties} if properties else {}),
        }

    def to_dict(self, source_ids: list[int]) -> dict[str, Any]:
        return {
            "source_ids": source_ids,
            "nodes": list(self._nodes.values()),
            "relationships": list(self._relationships.values()),
        }


def build_graph_from_analyses(
    sources: Iterable[Any],
    latest_analyses: dict[int, Any],
) -> dict[str, Any]:
    """Return the Knowledge Graph for the given sources.

    ``sources`` are ``Source`` rows and ``latest_analyses`` maps each source id
    to its most recent ``AnalysisResult``. Sources without an analysis still
    appear as document nodes so the user can see what is pending.
    """
    graph = GraphAccumulator()
    source_ids: list[int] = []
    # entity key -> set of source ids where the entity appears
    entity_sources: dict[tuple[str, str], set[int]] = {}
    entity_node_keys: dict[tuple[str, str], str] = {}

    for source in sources:
        source_ids.append(source.id)
        document_key = f"document:{source.id}"
        graph.add_node(
            document_key,
            "Document",
            {"source_id": source.id, "name": source.name},
        )

        analysis = latest_analyses.get(source.id)
        if analysis is None:
            continue

        for entity in analysis.entities or []:
            name = entity.get("value") or entity.get("name")
            entity_type = entity.get("type", "CONCEPT")
            if not name:
                continue

            key = _entity_key(name, entity_type)
            node_key = entity_node_keys.setdefault(
                key, f"entity:{key[1]}:{key[0]}"
            )
            graph.add_node(
                node_key,
                "Entity",
                {"name": str(name), "type": str(entity_type).upper()},
            )
            graph.add_relationship(node_key, "MENTIONED_IN", document_key)
            entity_sources.setdefault(key, set()).add(source.id)

        for relation in analysis.relations or []:
            source_name = relation.get("source")
            target_name = relation.get("target")
            if not source_name or not target_name:
                continue

            source_node = _find_entity_node(entity_node_keys, source_name)
            target_node = _find_entity_node(entity_node_keys, target_name)
            if source_node and target_node:
                graph.add_relationship(
                    source_node,
                    str(relation.get("relation") or "RELATED_TO"),
                    target_node,
                )

        for pattern in analysis.patterns or []:
            pattern_type = pattern.get("type", "UNKNOWN")
            description = pattern.get("description", "")
            pattern_key = f"pattern:{pattern_type}:{description}"
            graph.add_node(
                pattern_key,
                "Pattern",
                {"type": pattern_type, "description": description},
            )
            graph.add_relationship(pattern_key, "DETECTED_IN", document_key)

        for hypothesis in analysis.hypotheses or []:
            title = hypothesis.get("title", "Sin título")
            hypothesis_key = f"hypothesis:{source.id}:{title}"
            graph.add_node(
                hypothesis_key,
                "Hypothesis",
                {
                    "title": title,
                    "source_id": source.id,
                    "description": hypothesis.get("description", ""),
                    "confidence": hypothesis.get("confidence", 0),
                },
            )
            graph.add_relationship(
                hypothesis_key, "GENERATED_FROM", document_key
            )

    _link_documents_by_shared_entities(graph, entity_sources)
    return graph.to_dict(source_ids)


def _find_entity_node(
    entity_node_keys: dict[tuple[str, str], str], name: str
) -> str | None:
    normalized = " ".join(str(name).split()).lower()
    for (entity_name, _entity_type), node_key in entity_node_keys.items():
        if entity_name == normalized:
            return node_key
    return None


def _link_documents_by_shared_entities(
    graph: GraphAccumulator,
    entity_sources: dict[tuple[str, str], set[int]],
) -> None:
    """Connect documents that mention the same meaningful entities."""
    shared: dict[tuple[int, int], list[str]] = {}

    for (name, entity_type), source_ids in entity_sources.items():
        if entity_type in WEAK_LINK_TYPES or len(source_ids) < 2:
            continue
        ordered = sorted(source_ids)
        for index, first in enumerate(ordered):
            for second in ordered[index + 1:]:
                shared.setdefault((first, second), []).append(name)

    for (first, second), names in shared.items():
        graph.add_relationship(
            f"document:{first}",
            "SHARES_ENTITIES_WITH",
            f"document:{second}",
            {"shared_entities": sorted(names), "count": len(names)},
        )
