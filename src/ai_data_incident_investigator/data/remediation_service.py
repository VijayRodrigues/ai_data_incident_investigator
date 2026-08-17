from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.models import (
    RemediationAction,
    RemediationPriority,
    RemediationStatus,
)


def create_remediation_actions(
    session: Session,
    *,
    incident_id: UUID,
    finding_id: UUID,
    actions: list[str],
    priority: RemediationPriority = RemediationPriority.MEDIUM,
) -> list[RemediationAction]:
    remediation_actions: list[RemediationAction] = []

    for action_text in actions:
        action_text = action_text.strip()

        if not action_text:
            continue

        action = RemediationAction(
            id=uuid4(),
            incident_id=incident_id,
            finding_id=finding_id,
            action=action_text,
            priority=priority,
            status=RemediationStatus.PROPOSED,
        )

        session.add(action)
        remediation_actions.append(action)

    session.flush()

    return remediation_actions