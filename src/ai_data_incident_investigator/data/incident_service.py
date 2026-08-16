from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.models import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
)


def create_incident(
    session: Session,
    *,
    incident_number: str,
    title: str,
    description: str | None = None,
    severity: IncidentSeverity = IncidentSeverity.MEDIUM,
    status: IncidentStatus = IncidentStatus.OPEN,
    incident_type: IncidentType = IncidentType.OTHER,
    source_system: str | None = None,
    target_system: str | None = None,
    source_dataset: str | None = None,
    target_dataset: str | None = None,
    expected_record_count: int | None = None,
    actual_record_count: int | None = None,
    detected_at: datetime | None = None,
) -> Incident:
    difference_count = None

    if (
        expected_record_count is not None
        and actual_record_count is not None
    ):
        difference_count = (
            expected_record_count - actual_record_count
        )

    incident = Incident(
        incident_number=incident_number,
        title=title,
        description=description,
        severity=severity,
        status=status,
        incident_type=incident_type,
        source_system=source_system,
        target_system=target_system,
        source_dataset=source_dataset,
        target_dataset=target_dataset,
        expected_record_count=expected_record_count,
        actual_record_count=actual_record_count,
        difference_count=difference_count,
        detected_at=detected_at,
    )

    session.add(incident)
    session.flush()

    return incident


def get_incident(
    session: Session,
    incident_id: UUID,
) -> Incident | None:
    return session.get(Incident, incident_id)