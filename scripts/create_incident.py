from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.incident_service import create_incident
from ai_data_incident_investigator.data.models import IncidentType


def main() -> None:
    with Session(engine) as session:
        incident = create_incident(
            session,
            incident_number="INC-2026-000001",
            title="Customer record count discrepancy",
            description=(
                "The downstream customer dataset contains fewer "
                "records than expected."
            ),
            incident_type=IncidentType.RECORD_LOSS,
            source_system="customer_source",
            target_system="customer_reporting",
            source_dataset="customer_source.customer",
            target_dataset="customer_reporting.customer",
            expected_record_count=100000,
            actual_record_count=96800,
            detected_at=datetime.now(timezone.utc),
        )

        session.commit()

        print(f"Incident created: {incident.incident_number}")
        print(f"UUID: {incident.id}")
        print(f"Difference: {incident.difference_count}")


if __name__ == "__main__":
    main()