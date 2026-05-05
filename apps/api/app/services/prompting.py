"""Prompt construction utilities for provider requests."""

from textwrap import dedent


def build_diagnostic_prompt(target_url: str, query: str, competitor_urls: list[str]) -> str:
    """Build a stable prompt for cross-provider normalized AEO output."""
    competitors = "\n".join(f"- {item}" for item in competitor_urls) or "- none"
    return dedent(
        f"""
        You are an Amazon recommendation evaluator.
        Analyze how you would answer the user query and whether the target product appears in recommendations.

        Target URL:
        {target_url}

        User query:
        {query}

        Competitor URLs:
        {competitors}

        Return only valid JSON with this exact shape:
        {{
          "provider_name": "openai|anthropic|gemini",
          "model": "string",
          "answered_query": "string",
          "overall_verdict": "recommended|not_recommended|uncertain",
          "recommended_products": [
            {{"name":"string","url":"string|null","reason":"string","rank_hint":1}}
          ],
          "sentiment_score": 0,
          "relevance_score": 0,
          "trust_score": 0,
          "evidence_snippets": ["string"],
          "raw_answer_excerpt": "string",
          "suggested_improvements": {{
            "title": "string",
            "bullets": ["string"],
            "faqs": ["string"]
          }}
        }}

        Scoring guidance:
        - sentiment_score: positive framing and confidence in recommendation quality
        - relevance_score: query-product fit
        - trust_score: use of evidence, caution, and recommendation reliability
        """
    ).strip()

