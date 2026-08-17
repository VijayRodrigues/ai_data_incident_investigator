from sqlalchemy.orm import Session

from ai_data_incident_investigator.data.database import engine
from ai_data_incident_investigator.data.vector_search import search_evidence


INCIDENT_ID = "90313020-a51b-40c5-9576-ed0ba1d91a18"


def main() -> None:
    query = "customer records missing during pipeline processing"

    with Session(engine) as session:
        results = search_evidence(
            session,
            incident_id=INCIDENT_ID,
            query=query,
            limit=5,
        )

        print(f"Incident: {INCIDENT_ID}")
        print(f"Query: {query}")
        print(f"Results: {len(results)}")

        for result in results:
            print("\n---")
            print(f"Chunk: {result['chunk_index']}")
            print(f"Distance: {result['distance']}")
            print(f"Content: {result['content']}")


if __name__ == "__main__":
    main()