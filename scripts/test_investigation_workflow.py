from pprint import pprint

from sqlalchemy.orm import Session

from ai_data_incident_investigator.ai.investigator import (
    LLM_MODEL,
    investigate,
)
from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.investigation_service import (
    build_investigation_context,
    complete_investigation_run,
    create_finding,
    create_investigation_run,
    fail_investigation_run,
    link_finding_to_evidence,
)
from ai_data_incident_investigator.data.remediation_service import (
    create_remediation_actions,
)


INCIDENT_ID = "90313020-a51b-40c5-9576-ed0ba1d91a18"


def main() -> None:
    query = "customer records missing during pipeline processing"

    with Session(engine) as session:
        run = create_investigation_run(
            session,
            incident_id=INCIDENT_ID,
            model_name=LLM_MODEL,
        )

        try:
            context = build_investigation_context(
                session,
                incident_id=INCIDENT_ID,
                query=query,
                top_k=5,
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
                incident_id=INCIDENT_ID,
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

            print("\nINVESTIGATION COMPLETED")
            print("======================")
            print(f"Run ID: {run.id}")
            print(f"Finding ID: {finding.id}")
            print(f"Finding type: {finding.finding_type}")
            print(f"Severity: {finding.severity}")
            print(
                f"Confidence: {finding.confidence_score}"
            )

            print(
                f"Evidence links created: {len(evidence_links)}"
            )

            print(
                f"Remediation actions created: "
                f"{len(remediation_actions)}"
            )

            print("\nLINKED EVIDENCE:")
            for link in evidence_links:
                print(
                    f"  Chunk ID: {link.evidence_chunk_id}"
                )
                print(
                    f"  Distance: {link.relevance_distance}"
                )

            print("\nREMEDIATION ACTIONS:")
            for action in remediation_actions:
                print(
                    f"  [{action.priority}] "
                    f"{action.action}"
                )

            print("\nAI RESULT:")
            pprint(ai_result)

        except Exception as exc:
            session.rollback()

            print(
                f"Investigation failed: {exc}"
            )

            raise


if __name__ == "__main__":
    main()