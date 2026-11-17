from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db
from app.database.neo4j_connection import get_neo4j_driver, NEO4J_DATABASE
from app.models.user import User
from app.models.project import Project
from app.models.source import Source


router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"]
)


def build_graph(source_ids: list[int]):
    if not source_ids:
        return {
            "source_ids": [],
            "nodes": [],
            "relationships": []
        }

    try:
        neo4j_driver = get_neo4j_driver()

        with neo4j_driver.session(database=NEO4J_DATABASE) as session:
            node_result = session.run(
                """
                MATCH (d:Document)
                WHERE d.source_id IN $source_ids
                OPTIONAL MATCH (d)-[*1..2]-(n)
                WITH collect(DISTINCT d) + collect(DISTINCT n) AS raw_nodes
                UNWIND raw_nodes AS node
                WITH DISTINCT node
                WHERE node IS NOT NULL
                RETURN labels(node) AS labels, properties(node) AS properties
                """,
                source_ids=source_ids
            )

            nodes = [
                {
                    "labels": record["labels"],
                    "properties": record["properties"]
                }
                for record in node_result
            ]

            relationship_result = session.run(
                """
                MATCH p = (d:Document)-[*1..2]-(n)
                WHERE d.source_id IN $source_ids
                UNWIND relationships(p) AS relationship
                WITH DISTINCT relationship
                RETURN
                    properties(startNode(relationship)) AS source,
                    type(relationship) AS relation,
                    properties(endNode(relationship)) AS target
                """,
                source_ids=source_ids
            )

            relationships = [
                {
                    "source": record["source"],
                    "relation": record["relation"],
                    "target": record["target"]
                }
                for record in relationship_result
            ]

            return {
                "source_ids": source_ids,
                "nodes": nodes,
                "relationships": relationships
            }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge Graph no disponible: {str(exc)}"
        ) from exc


@router.get("/")
def get_general_graph(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sources = (
        db.query(Source)
        .join(Project, Source.project_id == Project.id)
        .filter(Project.user_id == current_user.id)
        .all()
    )
    return build_graph([source.id for source in sources])


@router.get("/project/{project_id}")
def get_project_graph(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Proyecto no encontrado"
        )

    sources = (
        db.query(Source)
        .filter(Source.project_id == project_id)
        .all()
    )
    return build_graph([source.id for source in sources])


@router.get("/source/{source_id}")
def get_source_graph(
    source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    source = (
        db.query(Source)
        .join(Project, Source.project_id == Project.id)
        .filter(
            Source.id == source_id,
            Project.user_id == current_user.id
        )
        .first()
    )

    if not source:
        raise HTTPException(
            status_code=404,
            detail="Fuente no encontrada"
        )

    return build_graph([source_id])
