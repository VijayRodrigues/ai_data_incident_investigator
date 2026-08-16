from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.database import engine

from ai_data_incident_investigator.data.incident_service import (
    create_incident,
    get_incident,
)

from ai_data_incident_investigator.data.models import (
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
)


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["incidents"],
)


def get_db():
    with Session(engine) as session:
        yield session


class IncidentCreate(BaseModel):
    incident_number: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None

    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    incident_type: IncidentType = IncidentType.OTHER

    source_system: str | None = None
    target_system: str | None = None

    source_dataset: str | None = None
    target_dataset: str | None = None

    expected_record_count: int | None = Field(
        default=None,
        ge=0,
    )

    actual_record_count: int | None = Field(
        default=None,
        ge=0,
    )

    detected_at: datetime | None = None


class IncidentResponse(BaseModel):
    id: UUID
    incident_number: str
    title: str
    severity: IncidentSeverity
    status: IncidentStatus
    incident_type: IncidentType
    difference_count: int | None

    model_config = {
        "from_attributes": True
    }


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=201,
)
def create_incident_endpoint(
    request: IncidentCreate,
    session: Session = Depends(get_db),
):
    incident = create_incident(
        session,
        incident_number=request.incident_number,
        title=request.title,
        description=request.description,
        severity=request.severity,
        status=IncidentStatus.OPEN,
        incident_type=request.incident_type,
        source_system=request.source_system,
        target_system=request.target_system,
        source_dataset=request.source_dataset,
        target_dataset=request.target_dataset,
        expected_record_count=request.expected_record_count,
        actual_record_count=request.actual_record_count,
        detected_at=request.detected_at,
    )

    session.commit()
    session.refresh(incident)

    return incident


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident_endpoint(
    incident_id: UUID,
    session: Session = Depends(get_db),
):


    incident = get_incident(session, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident