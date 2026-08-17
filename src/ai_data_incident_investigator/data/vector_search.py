from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.embedding_service import (
    generate_embedding,
)


def search_evidence(
    session: Session,
    *,
    incident_id: UUID,
    query: str,
    limit: int = 5,
):
    query_embedding = generate_embedding(query)

    sql = text(
        """
        SELECT
            ec.id,
            ec.evidence_id,
            ec.chunk_index,
            ec.content,
            ec.embedding_model,
            ec.embedding <=> CAST(:embedding AS vector) AS distance
        FROM evidence_chunks ec
        INNER JOIN evidence e
            ON e.id = ec.evidence_id
        WHERE e.incident_id = :incident_id
          AND ec.embedding IS NOT NULL
        ORDER BY ec.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
        """
    )

    result = session.execute(
        sql,
        {
            "embedding": str(query_embedding),
            "incident_id": str(incident_id),
            "limit": limit,
        },
    )

    return result.mappings().all()