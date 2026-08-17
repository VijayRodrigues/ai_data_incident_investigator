from uuid import UUID

from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.models import EvidenceChunk


def chunk_text(
    text: str,
    *,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    words = text.strip().split()

    if not words:
        return []

    chunks: list[str] = []
    current_words: list[str] = []
    current_length = 0

    for word in words:
        additional_length = len(word)

        if current_words:
            additional_length += 1

        if (
            current_words
            and current_length + additional_length > chunk_size
        ):
            chunks.append(" ".join(current_words))

            overlap_words: list[str] = []
            overlap_length = 0

            for previous_word in reversed(current_words):
                word_length = len(previous_word)

                if overlap_words:
                    word_length += 1

                if overlap_length + word_length > overlap:
                    break

                overlap_words.insert(0, previous_word)
                overlap_length += word_length

            current_words = overlap_words
            current_length = overlap_length

        current_words.append(word)

        if current_length:
            current_length += 1

        current_length += len(word) if current_length == len(word) else 0

        # Recalculate accurately.
        current_length = len(" ".join(current_words))

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def create_evidence_chunks(
    session: Session,
    *,
    evidence_id: UUID,
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[EvidenceChunk]:
    chunks = chunk_text(
        text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    evidence_chunks = []

    for index, content in enumerate(chunks):
        chunk = EvidenceChunk(
            evidence_id=evidence_id,
            chunk_index=index,
            content=content,
        )

        session.add(chunk)
        evidence_chunks.append(chunk)

    session.flush()

    return evidence_chunks