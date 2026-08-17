import json
from typing import Any

import ollama


LLM_MODEL = "qwen3:14b"


SYSTEM_PROMPT = """
You are an AI Data Incident Investigator.

Your job is to analyze a data incident using ONLY the incident
information and evidence provided to you.

Do not invent facts.
Do not assume facts that are not present in the evidence.
Clearly distinguish between:
- observed facts
- likely root causes
- recommendations

Return ONLY valid JSON.

The JSON must have exactly these fields:

{
  "finding_type": "...",
  "title": "...",
  "description": "...",
  "severity": "...",
  "confidence_score": 0.0,
  "is_root_cause_candidate": true,
  "evidence_summary": "...",
  "recommended_actions": [
    "..."
  ]
}

Allowed finding_type values:

- RECORD_LOSS
- FILTER
- JOIN
- SCHEMA
- FRESHNESS
- DUPLICATE
- DATA_QUALITY
- PIPELINE
- OTHER

Allowed severity values:

- LOW
- MEDIUM
- HIGH
- CRITICAL

confidence_score must be between 0.0 and 1.0.

The finding must be grounded in the supplied evidence.
"""


def investigate(context: dict[str, Any]) -> dict[str, Any]:
    prompt = f"""
Investigate the following data incident.

INCIDENT CONTEXT:

{json.dumps(context, indent=2, default=str)}

Analyze the incident and identify the most likely finding/root cause
supported by the supplied evidence.

Remember:
- Use only the supplied context.
- Do not invent missing pipeline steps.
- Do not claim certainty when the evidence does not support certainty.
- Return ONLY the required JSON object.
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format="json",
    )

    content = response["message"]["content"]

    result = json.loads(content)

    _validate_result(result)

    return result


def _validate_result(result: dict[str, Any]) -> None:
    required_fields = {
        "finding_type",
        "title",
        "description",
        "severity",
        "confidence_score",
        "is_root_cause_candidate",
        "evidence_summary",
        "recommended_actions",
    }

    missing = required_fields - result.keys()

    if missing:
        raise ValueError(
            f"Investigator response missing fields: {sorted(missing)}"
        )

    allowed_finding_types = {
        "RECORD_LOSS",
        "FILTER",
        "JOIN",
        "SCHEMA",
        "FRESHNESS",
        "DUPLICATE",
        "DATA_QUALITY",
        "PIPELINE",
        "OTHER",
    }

    allowed_severities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    if result["finding_type"] not in allowed_finding_types:
        raise ValueError(
            f"Invalid finding_type: {result['finding_type']}"
        )

    if result["severity"] not in allowed_severities:
        raise ValueError(
            f"Invalid severity: {result['severity']}"
        )

    confidence = float(result["confidence_score"])

    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            "confidence_score must be between 0.0 and 1.0"
        )

    if not isinstance(
        result["is_root_cause_candidate"],
        bool,
    ):
        raise ValueError(
            "is_root_cause_candidate must be boolean"
        )

    if not isinstance(
        result["recommended_actions"],
        list,
    ):
        raise ValueError(
            "recommended_actions must be a list"
        )