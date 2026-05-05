"""Scoring and recommendation analysis for AEO diagnostics."""

from __future__ import annotations

from statistics import mean

from app.schemas import ActionPlan, ProviderOutput, Scorecard, TargetAnalysis


def clamp_score(value: float) -> int:
    """Clamp floating score to integer in range [0, 100]."""
    return max(0, min(100, int(round(value))))


def compute_scorecard(providers: list[ProviderOutput], target_url: str) -> Scorecard:
    """Compute aggregate scorecard from provider outputs."""
    if not providers:
        return Scorecard(visibility=0, relevance=0, sentiment=0, trust=0, overall=0)
    visibility = clamp_score(_visibility_ratio(providers, target_url) * 100)
    relevance = clamp_score(mean(item.relevance_score for item in providers))
    sentiment = clamp_score(mean(item.sentiment_score for item in providers))
    trust = clamp_score(mean(item.trust_score for item in providers))
    overall = clamp_score((0.35 * visibility) + (0.30 * relevance) + (0.20 * sentiment) + (0.15 * trust))
    return Scorecard(
        visibility=visibility,
        relevance=relevance,
        sentiment=sentiment,
        trust=trust,
        overall=overall,
    )


def analyze_target_recommendation(providers: list[ProviderOutput], target_url: str) -> TargetAnalysis:
    """Analyze whether target listing is recommended and estimate best rank."""
    ranks: list[int] = []
    for provider in providers:
        for item in provider.recommended_products:
            if item.url and _normalized(item.url) == _normalized(target_url) and item.rank_hint:
                ranks.append(item.rank_hint)
    if not ranks:
        return TargetAnalysis(is_recommended=False, best_rank=None, confidence=40 if providers else 0)
    best_rank = min(ranks)
    confidence = 90 if len(ranks) >= 2 else 75
    return TargetAnalysis(is_recommended=True, best_rank=best_rank, confidence=confidence)


def merge_action_plan(providers: list[ProviderOutput]) -> ActionPlan:
    """Merge provider-level recommendations into prioritized action plan."""
    title_changes = _dedupe([item.suggested_improvements.title for item in providers])
    bullet_changes = _dedupe(
        [bullet for provider in providers for bullet in provider.suggested_improvements.bullets]
    )
    faq_changes = _dedupe(
        [faq for provider in providers for faq in provider.suggested_improvements.faqs]
    )
    priority_tasks = _build_priority_tasks(title_changes, bullet_changes, faq_changes)
    return ActionPlan(
        title_changes=title_changes[:5],
        bullet_changes=bullet_changes[:7],
        faq_changes=faq_changes[:7],
        priority_tasks=priority_tasks,
    )


def build_delta(current: Scorecard, baseline: Scorecard, recommendation_changed: bool) -> dict[str, int | bool]:
    """Compute rerun score deltas."""
    return {
        "overall_delta": current.overall - baseline.overall,
        "visibility_delta": current.visibility - baseline.visibility,
        "relevance_delta": current.relevance - baseline.relevance,
        "sentiment_delta": current.sentiment - baseline.sentiment,
        "trust_delta": current.trust - baseline.trust,
        "recommendation_changed": recommendation_changed,
    }


def _visibility_ratio(providers: list[ProviderOutput], target_url: str) -> float:
    seen = 0
    for provider in providers:
        for item in provider.recommended_products:
            if item.url and _normalized(item.url) == _normalized(target_url):
                seen += 1
                break
    return seen / len(providers)


def _normalized(url: object) -> str:
    value = str(url)
    return value.split("?")[0].rstrip("/")


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        candidate = item.strip()
        if candidate and candidate not in seen:
            seen.add(candidate)
            output.append(candidate)
    return output


def _build_priority_tasks(title: list[str], bullets: list[str], faqs: list[str]) -> list[str]:
    tasks: list[str] = []
    if title:
        tasks.append(f"Update listing title to emphasize: {title[0]}")
    if bullets:
        tasks.append(f"Rewrite top bullet around: {bullets[0]}")
    if faqs:
        tasks.append(f"Add FAQ answer for: {faqs[0]}")
    tasks.append("Re-run AEO report after edits and compare score movement.")
    return tasks[:4]
