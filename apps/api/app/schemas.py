"""Pydantic schemas for API contracts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class RecommendationItem(BaseModel):
    """Recommended product returned by a provider."""

    name: str
    url: HttpUrl | None
    reason: str
    rank_hint: int | None = Field(default=None, ge=1)


class SuggestedImprovements(BaseModel):
    """Provider-suggested listing improvements."""

    title: str
    bullets: list[str]
    faqs: list[str]


class ProviderOutput(BaseModel):
    """Normalized provider output schema."""

    provider_name: Literal["openai", "anthropic", "gemini"]
    model: str
    answered_query: str
    overall_verdict: Literal["recommended", "not_recommended", "uncertain"]
    recommended_products: list[RecommendationItem]
    sentiment_score: int = Field(ge=0, le=100)
    relevance_score: int = Field(ge=0, le=100)
    trust_score: int = Field(ge=0, le=100)
    evidence_snippets: list[str]
    raw_answer_excerpt: str
    suggested_improvements: SuggestedImprovements


class Scorecard(BaseModel):
    """Aggregated report scorecard."""

    visibility: int = Field(ge=0, le=100)
    relevance: int = Field(ge=0, le=100)
    sentiment: int = Field(ge=0, le=100)
    trust: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)


class TargetAnalysis(BaseModel):
    """Target listing recommendation analysis."""

    is_recommended: bool
    best_rank: int | None = None
    confidence: int = Field(ge=0, le=100)


class ActionPlan(BaseModel):
    """Merged listing optimization suggestions."""

    title_changes: list[str]
    bullet_changes: list[str]
    faq_changes: list[str]
    priority_tasks: list[str]


class DiagnosticRunRequest(BaseModel):
    """Run request payload."""

    target_url: HttpUrl
    query: str = Field(min_length=3, max_length=500)
    competitor_mode: Literal["manual", "auto"] = "auto"
    competitor_urls: list[HttpUrl] = Field(default_factory=list, max_length=5)
    baseline_run_id: str | None = None


class DiagnosticRunResponse(BaseModel):
    """Run response payload."""

    run_id: str
    created_at: datetime
    target_url: str
    query: str
    mode: Literal["live", "demo"]
    providers: list[ProviderOutput]
    scorecard: Scorecard
    target_analysis: TargetAnalysis
    action_plan: ActionPlan
    warnings: list[str]
    competitor_urls: list[str]


class RerunRequest(BaseModel):
    """Rerun request payload."""

    baseline_run_id: str
    target_url: HttpUrl
    query: str = Field(min_length=3, max_length=500)
    competitor_mode: Literal["manual", "auto"] = "auto"
    competitor_urls: list[HttpUrl] = Field(default_factory=list, max_length=5)


class DeltaReport(BaseModel):
    """Before/after delta summary for rerun."""

    baseline_run_id: str
    current_run_id: str
    overall_delta: int
    visibility_delta: int
    relevance_delta: int
    sentiment_delta: int
    trust_delta: int
    recommendation_changed: bool


class RerunResponse(BaseModel):
    """Rerun response payload."""

    run: DiagnosticRunResponse
    delta: DeltaReport
