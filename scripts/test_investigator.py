from pprint import pprint

from sqlalchemy.orm import Session

from ai_data_incident_investigator.ai.investigator import investigate
from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.investigation_service import (
    build_investigation_context,
)


INCIDENT_ID = "90313020-a51b-40c5-9576-ed0ba1d91a18"


def main() -> None:
    query = "customer records missing during pipeline processing"

    with Session(engine) as session:
        context = build_investigation_context(
            session,
            incident_id=INCIDENT_ID,
            query=query,
            top_k=5,
        )

    result = investigate(context)

    print("\nAI INVESTIGATION RESULT")
    print("=======================")

    pprint(result)


if __name__ == "__main__":
    main()