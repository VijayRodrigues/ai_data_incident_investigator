from uuid import uuid4

from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.models import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    EvidenceType,
)
from ai_data_incident_investigator.data.evidence_service import (
    create_evidence,
)
from ai_data_incident_investigator.data.evidence_chunking import (
    create_evidence_chunks,
)
from ai_data_incident_investigator.data.embedding_service import (
    embed_evidence_chunks,
)


INCIDENT_NUMBER = "INC-2026-000002"


EVIDENCE_TEXT = """
Pipeline validation and execution report

Pipeline: customer_source_to_customer_reporting
Execution status: COMPLETED_WITH_REJECTIONS

Source record count: 100000
Target record count: 96800
Rejected record count: 3200

Validation results:
- customer_type NULL: 3200 records
- customer_id NULL: 0 records
- customer_email invalid: 0 records
- Duplicate customer_id: 0 records

Target schema validation:
The target table customer_reporting.customer defines
customer_type as NOT NULL.

Rejection reason:
All 3200 records with customer_type = NULL failed target
schema validation because customer_type is required.

Pipeline behavior:
Records failing target schema validation were rejected
from downstream processing and were not loaded into the
target dataset.

Conclusion from pipeline execution:
3200 source records were rejected because customer_type
was NULL and violated the target NOT NULL constraint.
This resulted in the difference between the expected
100000 records and the actual 96800 records loaded.
""".strip()


def main() -> None:
    with Session(engine) as session:

        # ---------------------------------------------------------
        # 1. Create incident
        # ---------------------------------------------------------

        incident = Incident(
            id=uuid4(),
            incident_number=INCIDENT_NUMBER,
            title="Customer Records Rejected Due to NULL customer_type",
            description=(
                "3200 customer records were rejected during downstream "
                "processing because customer_type was NULL and violated "
                "the target NOT NULL constraint."
            ),
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.OPEN,
            incident_type=IncidentType.RECORD_LOSS,
            source_system="customer_source",
            target_system="customer_reporting",
            source_dataset="customer_source.customer",
            target_dataset="customer_reporting.customer",
            expected_record_count=100000,
            actual_record_count=96800,
            difference_count=3200,
        )

        session.add(incident)
        session.flush()

        print("Incident created")
        print(f"Incident ID: {incident.id}")
        print(f"Incident number: {incident.incident_number}")

        # ---------------------------------------------------------
        # 2. Create evidence
        # ---------------------------------------------------------

        evidence = create_evidence(
            session,
            incident_id=incident.id,
            title="Pipeline validation and execution report",
            description=(
                "Pipeline execution evidence showing the validation "
                "failure responsible for the rejected customer records."
            ),
            content=EVIDENCE_TEXT.encode("utf-8"),
            evidence_type=EvidenceType.LOG,
            source_system="customer_reporting",
            object_name=(
                f"incidents/{incident.incident_number}/"
                "pipeline_validation_report.txt"
            ),
        )

        print()
        print("Evidence created")
        print(f"Evidence ID: {evidence.id}")
        print(f"Storage URI: {evidence.storage_uri}")

        # ---------------------------------------------------------
        # 3. Chunk evidence
        # ---------------------------------------------------------

        chunks = create_evidence_chunks(
            session,
            evidence_id=evidence.id,
            text=EVIDENCE_TEXT,
            chunk_size=500,
            overlap=50,
        )

        print()
        print(f"Created {len(chunks)} evidence chunks")

        for chunk in chunks:
            print(
                f"Chunk {chunk.chunk_index}: "
                f"{chunk.content[:120]}..."
            )

        # ---------------------------------------------------------
        # 4. Generate BGE-M3 embeddings
        # ---------------------------------------------------------

        embedded_count = embed_evidence_chunks(
            session,
            evidence_id=evidence.id,
        )

        print()
        print(
            f"Embedded {embedded_count} evidence chunks "
            "using bge-m3."
        )

        # ---------------------------------------------------------
        # 5. Commit everything
        # ---------------------------------------------------------

        session.commit()

        print()
        print("ROOT CAUSE EVIDENCE CREATED")
        print("============================")
        print(f"Incident ID: {incident.id}")
        print(f"Incident number: {incident.incident_number}")
        print(f"Evidence ID: {evidence.id}")
        print(f"Chunks: {len(chunks)}")
        print(f"Embeddings: {embedded_count}")


if __name__ == "__main__":
    main()