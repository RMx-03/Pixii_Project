"""Unit tests for normalization helpers."""

from app.services.normalization import extract_json_object, normalize_provider_output


def _provider_payload() -> dict:
    return {
        "provider_name": "gemini",
        "model": "gemini-2.0-flash",
        "answered_query": "best portable blender for travel in India",
        "overall_verdict": "recommended",
        "recommended_products": [
            {
                "name": "Portable Blender",
                "url": "https://www.amazon.in/dp/B0F9YGHHXG",
                "reason": "Travel friendly and USB rechargeable",
                "rank_hint": 1,
            }
        ],
        "sentiment_score": 80,
        "relevance_score": 85,
        "trust_score": 75,
        "evidence_snippets": ["Rechargeable and compact design are highlighted."],
        "raw_answer_excerpt": "A compact and practical option for daily smoothies.",
        "suggested_improvements": {
            "title": "Emphasize travel and battery advantages",
            "bullets": ["Add runtime details", "Add cleaning convenience detail"],
            "faqs": ["How many blends per charge?"],
        },
    }


def test_extract_json_object_from_mixed_text() -> None:
    text = 'The answer is {"provider_name":"openai","model":"x"} end.'
    parsed = extract_json_object(text)
    assert parsed["provider_name"] == "openai"
    assert parsed["model"] == "x"


def test_normalize_provider_output_converts_fraction_scores_to_percent() -> None:
    payload = _provider_payload()
    payload["sentiment_score"] = 0.8
    payload["relevance_score"] = 0.9
    payload["trust_score"] = 0.7

    normalized = normalize_provider_output(payload)

    assert normalized.sentiment_score == 80
    assert normalized.relevance_score == 90
    assert normalized.trust_score == 70


def test_normalize_provider_output_clamps_and_rounds_scores() -> None:
    payload = _provider_payload()
    payload["sentiment_score"] = "101.9"
    payload["relevance_score"] = -5
    payload["trust_score"] = 73.6

    normalized = normalize_provider_output(payload)

    assert normalized.sentiment_score == 100
    assert normalized.relevance_score == 0
    assert normalized.trust_score == 74
