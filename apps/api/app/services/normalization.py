"""Provider response normalization logic."""

import json
import re
from typing import Any

from app.schemas import ProviderOutput


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
    return ProviderOutput.model_validate(payload)

