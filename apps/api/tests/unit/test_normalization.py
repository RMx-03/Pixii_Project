"""Unit tests for normalization helpers."""

from app.services.normalization import extract_json_object


def test_extract_json_object_from_mixed_text() -> None:
    text = 'The answer is {"provider_name":"openai","model":"x"} end.'
    parsed = extract_json_object(text)
    assert parsed["provider_name"] == "openai"
    assert parsed["model"] == "x"

