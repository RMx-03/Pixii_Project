"""Persistence helpers for diagnostic runs."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import DiagnosticRun, ProviderResponse
from app.schemas import DiagnosticRunResponse


def save_run(
    db: Session,
    response: DiagnosticRunResponse,
    provider_rows: list[ProviderResponse],
    target_url: str,
    query: str,
    competitor_mode: str,
    competitor_urls: list[str],
    baseline_run_id: str | None,
) -> DiagnosticRun:
    """Persist diagnostic run and provider-level rows."""
    run = DiagnosticRun(
        target_url=target_url,
        query=query,
        competitor_mode=competitor_mode,
        competitor_urls=competitor_urls,
        baseline_run_id=baseline_run_id,
        is_demo=response.mode == "demo",
        report_json=response.model_dump(mode="json"),
        score_json=response.scorecard.model_dump(mode="json"),
    )
    for row in provider_rows:
        run.provider_responses.append(row)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_run_or_none(db: Session, run_id: str) -> DiagnosticRun | None:
    """Fetch run by id."""
    return db.query(DiagnosticRun).filter(DiagnosticRun.id == run_id).first()
