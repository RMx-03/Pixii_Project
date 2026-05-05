"""Unit tests for scoring logic."""

from app.schemas import ProviderOutput
from app.services.scoring import analyze_target_recommendation, compute_scorecard


def _provider(provider_name: str, rank_hint: int | None) -> ProviderOutput:
    return ProviderOutput.model_validate(
        {
            "provider_name": provider_name,
            "model": "test-model",
            "answered_query": "best magnesium supplement for seniors",
            "overall_verdict": "recommended" if rank_hint else "uncertain",
            "recommended_products": (
                [
                    {
                        "name": "Target",
                        "url": "https://www.amazon.com/dp/B000TEST",
                        "reason": "Strong fit",
                        "rank_hint": rank_hint,
                    }
                ]
                if rank_hint
                else []
            ),
            "sentiment_score": 70,
            "relevance_score": 80,
            "trust_score": 75,
            "evidence_snippets": ["Evidence"],
            "raw_answer_excerpt": "Excerpt",
            "suggested_improvements": {
                "title": "Improve title",
                "bullets": ["Improve bullet"],
                "faqs": ["Improve faq"],
            },
        }
    )


def test_compute_scorecard_visibility_and_overall() -> None:
    providers = [
        _provider("openai", 1),
        _provider("anthropic", None),
        _provider("gemini", 2),
    ]
    score = compute_scorecard(providers, target_url="https://www.amazon.com/dp/B000TEST")
    assert score.visibility == 67
    assert score.relevance == 80
    assert score.sentiment == 70
    assert score.trust == 75
    assert score.overall > 0


def test_target_recommendation_rank_detection() -> None:
    providers = [_provider("openai", 3), _provider("gemini", 2)]
    analysis = analyze_target_recommendation(providers, target_url="https://www.amazon.com/dp/B000TEST")
    assert analysis.is_recommended
    assert analysis.best_rank == 2
    assert analysis.confidence >= 75

