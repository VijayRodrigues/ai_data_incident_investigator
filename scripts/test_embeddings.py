from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.embedding_service import (
    embed_evidence_chunks,
)


EVIDENCE_ID = "ca1f9964-1726-485d-8e58-1dec7d4aed26"


def main() -> None:
    with Session(engine) as session:
        count = embed_evidence_chunks(
            session,
            evidence_id=EVIDENCE_ID,
        )

        session.commit()

        print(f"Embedded {count} evidence chunks.")
        print("Embedding model: bge-m3")
        print("Embedding dimensions: 1024")


if __name__ == "__main__":
    main()