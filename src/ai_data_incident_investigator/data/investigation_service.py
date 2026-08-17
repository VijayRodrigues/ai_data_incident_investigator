from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.models import (
    Finding,
    FindingEvidence,
    InvestigationRun,
    InvestigationStatus,
    InvestigatorType,
)
from ai_data_incident_investigator.data.vector_search import search_evidence


def build_investigation_context(
    session: Session,
    *,
    incident_id: UUID,
    query: str,
    top_k: int = 5,
) -> dict:
    incident_sql = text(
        """
        SELECT
            id,
            incident_number,
            title,
            description,
            severity,
            status,
            incident_type,
            source_system,
            target_system,
            source_dataset,
            target_dataset,
            expected_record_count,
            actual_record_count,
            difference_count,
            detected_at,
            resolved_at
        FROM incidents
        WHERE id = :incident_id
        """
    )

    incident_result = session.execute(
        incident_sql,
        {"incident_id": str(incident_id)},
    ).mappings().first()

    if incident_result is None:
        raise ValueError(
            f"Incident {incident_id} not found."
        )

    evidence_results = search_evidence(
        session,
        incident_id=incident_id,
        query=query,
        limit=top_k,
    )

    evidence = []

    for result in evidence_results:
        evidence.append(
            {
                "evidence_chunk_id": str(result["id"]),
                "evidence_id": str(result["evidence_id"]),
                "chunk_index": result["chunk_index"],
                "content": result["content"],
                "embedding_model": result["embedding_model"],
                "distance": float(result["distance"]),
            }
        )

    return {
        "incident": {
            "id": str(incident_result["id"]),
            "incident_number": incident_result["incident_number"],
            "title": incident_result["title"],
            "description": incident_result["description"],
            "severity": incident_result["severity"],
            "status": incident_result["status"],
            "incident_type": incident_result["incident_type"],
            "source_system": incident_result["source_system"],
            "target_system": incident_result["target_system"],
            "source_dataset": incident_result["source_dataset"],
            "target_dataset": incident_result["target_dataset"],
            "expected_record_count": incident_result[
                "expected_record_count"
            ],
            "actual_record_count": incident_result[
                "actual_record_count"
            ],
            "difference_count": incident_result[
                "difference_count"
            ],
            "detected_at": incident_result["detected_at"],
            "resolved_at": incident_result["resolved_at"],
        },
        "retrieval": {
            "query": query,
            "top_k": top_k,
            "results_returned": len(evidence),
        },
        "evidence": evidence,
    }


def create_investigation_run(
    session: Session,
    *,
    incident_id: UUID,
    model_name: str,
) -> InvestigationRun:
    previous_run_count = (
        session.query(InvestigationRun)
        .filter(
            InvestigationRun.incident_id == incident_id
        )
        .count()
    )

    run = InvestigationRun(
        id=uuid4(),
        incident_id=incident_id,
        run_number=previous_run_count + 1,
        status=InvestigationStatus.RUNNING,
        investigator_type=InvestigatorType.AI,
        model_name=model_name,
    )

    session.add(run)
    session.flush()

    return run


def complete_investigation_run(
    session: Session,
    *,
    run: InvestigationRun,
    summary: str,
    confidence_score: float,
) -> None:
    run.status = InvestigationStatus.COMPLETED
    run.summary = summary
    run.confidence_score = confidence_score
    run.completed_at = datetime.now(timezone.utc)


def fail_investigation_run(
    session: Session,
    *,
    run: InvestigationRun,
    error_message: str,
) -> None:
    run.status = InvestigationStatus.FAILED
    run.summary = error_message
    run.completed_at = datetime.now(timezone.utc)


def create_finding(
    session: Session,
    *,
    investigation_run_id: UUID,
    finding_type: str,
    title: str,
    description: str,
    severity: str,
    confidence_score: float,
    is_root_cause_candidate: bool,
    evidence_summary: str | None = None,
) -> Finding:
    finding = Finding(
        id=uuid4(),
        investigation_run_id=investigation_run_id,
        finding_type=finding_type,
        title=title,
        description=description,
        severity=severity,
        confidence_score=confidence_score,
        is_root_cause_candidate=is_root_cause_candidate,
        evidence_summary=evidence_summary,
    )

    session.add(finding)
    session.flush()

    return finding


def link_finding_to_evidence(
    session: Session,
    *,
    finding: Finding,
    evidence: list[dict],
) -> list[FindingEvidence]:
    links: list[FindingEvidence] = []

    for item in evidence:
        evidence_chunk_id = UUID(
            str(item["evidence_chunk_id"])
        )

        relevance_distance = item.get("distance")

        link = FindingEvidence(
            id=uuid4(),
            finding_id=finding.id,
            evidence_chunk_id=evidence_chunk_id,
            relevance_distance=(
                float(relevance_distance)
                if relevance_distance is not None
                else None
            ),
        )

        session.add(link)
        links.append(link)

    session.flush()

    return links