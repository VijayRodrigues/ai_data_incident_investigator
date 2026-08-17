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


INCIDENT_NUMBER = "INC-2026-000003"


EVIDENCE_TEXT = """
Pipeline execution report

Pipeline: customer_source_to_customer_reporting
Execution status: COMPLETED_WITH_REJECTIONS

Source record count: 100000
Target record count: 96800
Rejected record count: 3200

The pipeline completed successfully but 3200 records were
not present in the target dataset.

No rejection reason was recorded in the available execution
report.

No validation error details are available.

No target schema information is available.

No transformation or filtering details are available.

No information is available about the contents of the
rejected records.

The available evidence confirms that 3200 records were
rejected or otherwise excluded, but does not establish why
the records were rejected or excluded.
""".strip()


def main() -> None:
    with Session(engine) as session:

        incident = Incident(
            id=uuid4(),
            incident_number=INCIDENT_NUMBER,
            title="3200 Customer Records Missing From Target",
            description=(
                "3200 customer records are missing from the target "
                "dataset, but the available evidence does not identify "
                "the cause."
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

        evidence = create_evidence(
            session,
            incident_id=incident.id,
            title="Pipeline execution report - insufficient evidence",
            description=(
                "Pipeline execution evidence confirming record loss "
                "without identifying the rejection cause."
            ),
            content=EVIDENCE_TEXT.encode("utf-8"),
            evidence_type=EvidenceType.LOG,
            source_system="customer_reporting",
            object_name=(
                f"incidents/{incident.incident_number}/"
                "pipeline_execution_report.txt"
            ),
        )

        print()
        print("Evidence created")
        print(f"Evidence ID: {evidence.id}")

        chunks = create_evidence_chunks(
            session,
            evidence_id=evidence.id,
            text=EVIDENCE_TEXT,
            chunk_size=500,
            overlap=50,
        )

        print()
        print(f"Created {len(chunks)} evidence chunks")

        embedded_count = embed_evidence_chunks(
            session,
            evidence_id=evidence.id,
        )

        print()
        print(
            f"Embedded {embedded_count} evidence chunks "
            "using bge-m3."
        )

        session.commit()

        print()
        print("INSUFFICIENT-EVIDENCE TEST DATA CREATED")
        print("=======================================")
        print(f"Incident ID: {incident.id}")
        print(f"Incident number: {incident.incident_number}")
        print(f"Evidence ID: {evidence.id}")
        print(f"Chunks: {len(chunks)}")
        print(f"Embeddings: {embedded_count}")


if __name__ == "__main__":
    main()