from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ai_data_incident_investigator.ai.investigator import (
    LLM_MODEL,
    investigate,
)
from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.incident_service import (
    get_incident,
)
from ai_data_incident_investigator.data.investigation_service import (
    build_investigation_context,
    complete_investigation_run,
    create_finding,
    create_investigation_run,
    link_finding_to_evidence,
)
from ai_data_incident_investigator.data.remediation_service import (
    create_remediation_actions,
)
from ai_data_incident_investigator.data.models import (
    InvestigationRun,
)


router = APIRouter(
    prefix="/api/v1/incidents",
    tags=["investigations"],
)


def get_db():
    with Session(engine) as session:
        yield session


class InvestigationRequest(BaseModel):
    query: str = Field(
        default="customer records missing during pipeline processing",
        min_length=1,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class EvidenceLinkResponse(BaseModel):
    evidence_chunk_id: UUID
    relevance_distance: float | None


class RemediationActionResponse(BaseModel):
    id: UUID
    action: str
    priority: str
    status: str


class FindingResponse(BaseModel):
    id: UUID
    finding_type: str
    title: str
    description: str
    severity: str
    confidence_score: float | None
    is_root_cause_candidate: bool
    evidence_summary: str | None


class InvestigationResponse(BaseModel):
    investigation_run_id: UUID
    finding_id: UUID

    finding_type: str
    title: str
    description: str
    severity: str
    confidence_score: float | None
    is_root_cause_candidate: bool
    evidence_summary: str | None

    evidence_links: list[EvidenceLinkResponse]
    remediation_actions: list[RemediationActionResponse]


class InvestigationHistoryItem(BaseModel):
    investigation_run_id: UUID
    incident_id: UUID
    run_number: int
    status: str
    investigator_type: str
    model_name: str
    summary: str | None
    confidence_score: float | None
    started_at: object | None
    completed_at: object | None
    findings: list[FindingResponse]


class InvestigationHistoryResponse(BaseModel):
    incident_id: UUID
    investigations: list[InvestigationHistoryItem]


@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationResponse,
)
def investigate_incident(
    incident_id: UUID,
    request: InvestigationRequest,
    session: Session = Depends(get_db),
):
    incident = get_incident(
        session,
        incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    run = create_investigation_run(
        session,
        incident_id=incident_id,
        model_name=LLM_MODEL,
    )

    try:
        context = build_investigation_context(
            session,
            incident_id=incident_id,
            query=request.query,
            top_k=request.top_k,
        )

        if not context["evidence"]:
            raise ValueError(
                "No evidence was found for this incident."
            )

        ai_result = investigate(context)

        finding = create_finding(
            session,
            investigation_run_id=run.id,
            finding_type=ai_result["finding_type"],
            title=ai_result["title"],
            description=ai_result["description"],
            severity=ai_result["severity"],
            confidence_score=ai_result["confidence_score"],
            is_root_cause_candidate=ai_result[
                "is_root_cause_candidate"
            ],
            evidence_summary=ai_result[
                "evidence_summary"
            ],
        )

        evidence_links = link_finding_to_evidence(
            session,
            finding=finding,
            evidence=context["evidence"],
        )

        remediation_actions = create_remediation_actions(
            session,
            incident_id=incident_id,
            finding_id=finding.id,
            actions=ai_result["recommended_actions"],
        )

        complete_investigation_run(
            session,
            run=run,
            summary=ai_result["description"],
            confidence_score=ai_result[
                "confidence_score"
            ],
        )

        session.commit()

        return InvestigationResponse(
            investigation_run_id=run.id,
            finding_id=finding.id,
            finding_type=finding.finding_type.value,
            title=finding.title,
            description=finding.description,
            severity=finding.severity.value,
            confidence_score=(
                float(finding.confidence_score)
                if finding.confidence_score is not None
                else None
            ),
            is_root_cause_candidate=(
                finding.is_root_cause_candidate
            ),
            evidence_summary=finding.evidence_summary,
            evidence_links=[
                EvidenceLinkResponse(
                    evidence_chunk_id=link.evidence_chunk_id,
                    relevance_distance=(
                        float(link.relevance_distance)
                        if link.relevance_distance is not None
                        else None
                    ),
                )
                for link in evidence_links
            ],
            remediation_actions=[
                RemediationActionResponse(
                    id=action.id,
                    action=action.action,
                    priority=action.priority.value,
                    status=action.status.value,
                )
                for action in remediation_actions
            ],
        )

    except Exception as exc:
        session.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {exc}",
        )


@router.get(
    "/{incident_id}/investigations",
    response_model=InvestigationHistoryResponse,
)
def get_investigation_history(
    incident_id: UUID,
    session: Session = Depends(get_db),
):
    incident = get_incident(
        session,
        incident_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    runs = (
        session.query(InvestigationRun)
        .filter(
            InvestigationRun.incident_id == incident_id
        )
        .order_by(
            InvestigationRun.run_number.desc()
        )
        .all()
    )

    history = []

    for run in runs:
        findings = []

        for finding in run.findings:
            findings.append(
                FindingResponse(
                    id=finding.id,
                    finding_type=finding.finding_type.value,
                    title=finding.title,
                    description=finding.description,
                    severity=finding.severity.value,
                    confidence_score=(
                        float(finding.confidence_score)
                        if finding.confidence_score is not None
                        else None
                    ),
                    is_root_cause_candidate=(
                        finding.is_root_cause_candidate
                    ),
                    evidence_summary=finding.evidence_summary,
                )
            )

        history.append(
            InvestigationHistoryItem(
                investigation_run_id=run.id,
                incident_id=run.incident_id,
                run_number=run.run_number,
                status=run.status.value,
                investigator_type=run.investigator_type.value,
                model_name=run.model_name,
                summary=run.summary,
                confidence_score=(
                    float(run.confidence_score)
                    if run.confidence_score is not None
                    else None
                ),
                started_at=run.started_at,
                completed_at=run.completed_at,
                findings=findings,
            )
        )

    return InvestigationHistoryResponse(
        incident_id=incident_id,
        investigations=history,
    )