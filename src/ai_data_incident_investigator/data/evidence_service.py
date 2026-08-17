import hashlib
from uuid import UUID

from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.models import (
    Evidence,
    EvidenceType,
)
from ai_data_incident_investigator.data.object_storage import upload_bytes


def create_evidence(
    session: Session,
    *,
    incident_id: UUID,
    title: str,
    content: bytes,
    evidence_type: EvidenceType,
    source_system: str | None = None,
    description: str | None = None,
    object_name: str,
) -> Evidence:
    content_hash = hashlib.sha256(content).hexdigest()

    upload_bytes(
        content,
        object_name,
    )

    evidence = Evidence(
        incident_id=incident_id,
        evidence_type=evidence_type,
        title=title,
        description=description,
        storage_uri=f"minio://ai-incident-investigator/{object_name}",
        source_system=source_system,
        content_hash=content_hash,
    )

    session.add(evidence)
    session.flush()

    return evidence