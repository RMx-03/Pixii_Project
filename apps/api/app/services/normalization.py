"""Provider response normalization logic."""

import json
import math
import re
from typing import Any

from app.schemas import ProviderOutput

SCORE_FIELDS = ("sentiment_score", "relevance_score", "trust_score")


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from mixed provider text."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def normalize_provider_output(payload: dict[str, Any]) -> ProviderOutput:
    """Normalize arbitrary provider payload to strict response schema."""
    normalized_payload = dict(payload)
    for field_name in SCORE_FIELDS:
        if field_name in normalized_payload:
            normalized_payload[field_name] = _coerce_percentage_score(
                normalized_payload[field_name], field_name
            )
    return ProviderOutput.model_validate(normalized_payload)


def _coerce_percentage_score(raw_value: Any, field_name: str) -> int:
    """Coerce provider score values to integer percentages in [0, 100]."""
    if isinstance(raw_value, bool):
        raise ValueError(f"{field_name} must be a numeric score, not a boolean")

    numeric_value: float
    if isinstance(raw_value, int | float):
        numeric_value = float(raw_value)
    elif isinstance(raw_value, str):
        value_text = raw_value.strip()
        if not value_text:
            raise ValueError(f"{field_name} cannot be empty")
        try:
            numeric_value = float(value_text)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be numeric, got {raw_value!r}") from exc
    else:
        raise ValueError(f"{field_name} must be numeric, got {type(raw_value).__name__}")

    if not math.isfinite(numeric_value):
        raise ValueError(f"{field_name} must be finite")

    if 0.0 <= numeric_value <= 1.0:
        numeric_value *= 100.0

    bounded = max(0.0, min(100.0, numeric_value))
    return int(round(bounded))
