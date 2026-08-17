from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.evidence_service import create_evidence
from ai_data_incident_investigator.data.models import EvidenceType


INCIDENT_ID = "90313020-a51b-40c5-9576-ed0ba1d91a18"


def main() -> None:
    content = b"""Pipeline execution report

Expected records: 100000
Actual records: 96800
Rejected records: 3200

Investigation note:
Customer records were lost during downstream processing.
"""

    with Session(engine) as session:
        evidence = create_evidence(
            session,
            incident_id=INCIDENT_ID,
            title="Pipeline execution report",
            content=content,
            evidence_type=EvidenceType.LOG,
            source_system="customer_reporting",
            description="Pipeline execution evidence for the record-loss incident.",
            object_name=f"{INCIDENT_ID}/evidence/pipeline_execution_report.txt",
        )

        session.commit()

        print(f"Evidence created: {evidence.id}")
        print(f"Storage URI: {evidence.storage_uri}")
        print(f"SHA-256: {evidence.content_hash}")


if __name__ == "__main__":
    main()