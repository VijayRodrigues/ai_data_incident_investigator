from fastapi import FastAPI

from ai_data_incident_investigator.api.incidents import (
    router as incidents_router,
)
from ai_data_incident_investigator.api.investigations import (
    router as investigations_router,
)


app = FastAPI(
    title="AI Data Incident Investigator",
    version="0.1.0",
)


app.include_router(incidents_router)
app.include_router(investigations_router)


@app.get("/health")
def health():
    return {"status": "healthy"}