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

IMPORTANT ROOT-CAUSE RULES:

- State what the supplied evidence directly proves.
- Identify a likely technical root cause only when the evidence
  supports a causal relationship.
- Do not call a cause a confirmed root cause unless the evidence
  directly establishes that relationship.
- If the evidence establishes a technical mechanism but does not
  establish whether that mechanism was intended or correct, say so.
- Never describe pipeline behavior as "correct", "expected",
  "intended", or "appropriate" unless the supplied evidence
  explicitly supports that conclusion.
- Do not confuse the incident symptom with its root cause.
- A record-count discrepancy or rejected-record count is an
  observed impact/symptom. Look for evidence explaining WHY
  the records were rejected.
- If the evidence is insufficient to establish a root cause,
  set is_root_cause_candidate to false.
- Do not invent missing pipeline steps, business rules,
  transformation logic, or system behavior.

For example:

Observed fact:
3200 records were rejected.

Supported likely cause:
3200 records had customer_type = NULL and the target schema
requires customer_type NOT NULL.

Unsupported assumption:
The pipeline was "correct" to reject those records.

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

Before producing the final JSON, reason about the distinction between:

1. What happened?
2. What evidence directly proves it?
3. What technical mechanism most likely caused it?
4. What remains unproven?

Your final description must not present an inference as an established
fact.

Remember:

- Use only the supplied context.
- Do not invent missing pipeline steps.
- Do not assume that a rejection was intentional or correct unless
  the evidence explicitly proves that.
- Do not claim certainty when the evidence does not support certainty.
- Treat record-count differences and rejected-record counts as
  symptoms/impacts unless the evidence explains their cause.
- If the evidence directly links a validation rule, schema constraint,
  transformation, filter, join, or other mechanism to the incident,
  identify that mechanism as the likely root cause.
- If the evidence does not establish a root cause, set
  is_root_cause_candidate to false.
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