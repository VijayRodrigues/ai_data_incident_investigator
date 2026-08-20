# AI Data Incident Investigator

An end-to-end data engineering and AI system for detecting, investigating,
and explaining data incidents using evidence from data pipelines,
quality checks, metadata, documentation, and historical incidents. 

## Architecture

Local development:
- Python
- PySpark
- PostgreSQL + pgvector
- MinIO
- Airflow
- Ollama
- FastAPI
- Streamlit
- Docker

Azure:
- ADLS Gen2
- Azure Databricks
- Unity Catalog
- Delta Lake
- Databricks Jobs
- Azure Key Vault
- Azure Monitor

## Project Goals

1. Detect data incidents.
2. Collect deterministic evidence.
3. Investigate incidents using AI-assisted reasoning.
4. Retrieve relevant documentation and historical incidents.
5. Produce evidence-backed root-cause analysis.
6. Recommend remediation without allowing uncontrolled production changes.
7. Maintain reproducible investigation traces.
8. Evaluate AI investigation quality.

## Status

Phase 1 — Foundation Setup
