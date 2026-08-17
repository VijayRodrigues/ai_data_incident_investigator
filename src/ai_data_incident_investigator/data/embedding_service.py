from uuid import UUID

import ollama
from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.models import EvidenceChunk


EMBEDDING_MODEL = "bge-m3"


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    embedding = response["embeddings"][0]

    if len(embedding) != 1024:
        raise ValueError(
            f"Expected 1024 dimensions, got {len(embedding)}."
        )

    return embedding


def embed_evidence_chunks(
    session: Session,
    *,
    evidence_id: UUID,
) -> int:
    chunks = (
        session.query(EvidenceChunk)
        .filter(EvidenceChunk.evidence_id == evidence_id)
        .order_by(EvidenceChunk.chunk_index)
        .all()
    )

    if not chunks:
        raise ValueError(
            f"No evidence chunks found for evidence {evidence_id}."
        )

    for chunk in chunks:
        chunk.embedding = generate_embedding(chunk.content)
        chunk.embedding_model = EMBEDDING_MODEL

    session.flush()

    return len(chunks)