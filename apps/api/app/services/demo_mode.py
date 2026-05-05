"""Deterministic demo-mode output for missing provider keys."""

from __future__ import annotations

from app.schemas import ProviderOutput


def build_demo_provider_outputs(query: str, target_url: str) -> list[ProviderOutput]:
    """Return deterministic provider outputs for demo fallback mode."""
    base = [
        {
            "provider_name": "openai",
            "model": "demo-gpt",
            "answered_query": query,
            "overall_verdict": "uncertain",
            "recommended_products": [
                {
                    "name": "Target Product",
                    "url": target_url,
                    "reason": "Target appears relevant but missing senior-focused evidence.",
                    "rank_hint": 3,
                }
            ],
            "sentiment_score": 68,
            "relevance_score": 72,
            "trust_score": 66,
            "evidence_snippets": [
                "The formula appears appropriate, but age-specific dosage guidance is unclear."
            ],
            "raw_answer_excerpt": "This product may fit some users but needs stronger proof points.",
            "suggested_improvements": {
                "title": "Highlight age-specific magnesium form and dosage clarity",
                "bullets": [
                    "State clinically relevant magnesium type for seniors",
                    "Add absorption and tolerability message"
                ],
                "faqs": [
                    "Is this magnesium suitable for adults over 60?",
                    "What is the recommended daily serving for seniors?"
                ]
            },
        },
        {
            "provider_name": "anthropic",
            "model": "demo-claude",
            "answered_query": query,
            "overall_verdict": "not_recommended",
            "recommended_products": [],
            "sentiment_score": 54,
            "relevance_score": 63,
            "trust_score": 71,
            "evidence_snippets": ["Competitor listings provide clearer ingredient transparency."],
            "raw_answer_excerpt": "I would prioritize options with stronger evidence presentation.",
            "suggested_improvements": {
                "title": "Increase clinical and ingredient transparency in title",
                "bullets": [
                    "Quantify elemental magnesium clearly",
                    "Add quality certifications and testing statements"
                ],
                "faqs": [
                    "How is purity validated?",
                    "Is this easy on sensitive stomachs?"
                ]
            },
        },
        {
            "provider_name": "gemini",
            "model": "demo-gemini",
            "answered_query": query,
            "overall_verdict": "recommended",
            "recommended_products": [
                {
                    "name": "Target Product",
                    "url": target_url,
                    "reason": "Balanced formulation and positive sentiment if improved positioning is added.",
                    "rank_hint": 2,
                }
            ],
            "sentiment_score": 74,
            "relevance_score": 78,
            "trust_score": 69,
            "evidence_snippets": ["Clearer FAQs would likely increase answer-engine confidence."],
            "raw_answer_excerpt": "The listing can become highly competitive with clearer proof claims.",
            "suggested_improvements": {
                "title": "Emphasize senior support and absorption benefits",
                "bullets": [
                    "Add direct benefit statement for sleep and muscle support",
                    "Reference dosage convenience and quality controls"
                ],
                "faqs": [
                    "Can this be taken with common senior supplements?",
                    "How long before noticeable results?"
                ]
            },
        },
    ]
    return [ProviderOutput.model_validate(item) for item in base]

