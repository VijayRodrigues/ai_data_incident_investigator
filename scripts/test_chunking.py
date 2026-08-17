from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.evidence_chunking import (
    create_evidence_chunks,
)
from ai_data_incident_investigator.data.object_storage import download_bytes


EVIDENCE_ID = "ca1f9964-1726-485d-8e58-1dec7d4aed26"

OBJECT_NAME = (
    "90313020-a51b-40c5-9576-ed0ba1d91a18/"
    "evidence/pipeline_execution_report.txt"
)


def main() -> None:
    content = download_bytes(OBJECT_NAME)
    text = content.decode("utf-8")

    with Session(engine) as session:
        chunks = create_evidence_chunks(
            session,
            evidence_id=EVIDENCE_ID,
            text=text,
            chunk_size=100,
            overlap=20,
        )

        session.commit()

        print(f"Created {len(chunks)} chunks")

        for chunk in chunks:
            print(f"\nChunk {chunk.chunk_index}:")
            print(chunk.content)


if __name__ == "__main__":
    main()