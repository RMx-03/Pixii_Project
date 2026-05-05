"""Diagnostic endpoints for run, rerun, export, and retrieval."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import DiagnosticRun
from app.persistence import get_run_or_none, save_run
from app.schemas import (
    DeltaReport,
    DiagnosticRunRequest,
    DiagnosticRunResponse,
    RerunRequest,
    RerunResponse,
)
from app.services.exporter import render_markdown, render_pdf
from app.services.orchestrator import DiagnosticOrchestrator
from app.services.scoring import build_delta

router = APIRouter()


@router.post("/run", response_model=DiagnosticRunResponse)
async def run_diagnostic(payload: DiagnosticRunRequest, db: Session = Depends(get_db)) -> DiagnosticRunResponse:
    """Create a new AEO diagnostic run."""
    settings = get_settings()
    orchestrator = DiagnosticOrchestrator(settings)
    response, provider_rows, _ = await orchestrator.run_diagnostic(
        target_url=str(payload.target_url),
        query=payload.query,
        competitor_mode=payload.competitor_mode,
        competitor_urls=[str(item) for item in payload.competitor_urls],
    )
    run = save_run(
        db=db,
        response=response,
        provider_rows=provider_rows,
        target_url=str(payload.target_url),
        query=payload.query,
        competitor_mode=payload.competitor_mode,
        competitor_urls=response.competitor_urls,
        baseline_run_id=payload.baseline_run_id,
    )
    saved = response.model_copy(update={"run_id": run.id, "created_at": run.created_at})
    run.report_json = saved.model_dump(mode="json")
    db.add(run)
    db.commit()
    return saved


@router.post("/rerun", response_model=RerunResponse)
async def rerun_diagnostic(payload: RerunRequest, db: Session = Depends(get_db)) -> RerunResponse:
    """Create a rerun and return score delta against baseline."""
    baseline = get_run_or_none(db, payload.baseline_run_id)
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline run not found")

    run_request = DiagnosticRunRequest(
        target_url=payload.target_url,
        query=payload.query,
        competitor_mode=payload.competitor_mode,
        competitor_urls=payload.competitor_urls,
        baseline_run_id=payload.baseline_run_id,
    )
    current = await run_diagnostic(run_request, db)
    baseline_report = DiagnosticRunResponse.model_validate(baseline.report_json)
    delta_payload = build_delta(
        current=current.scorecard,
        baseline=baseline_report.scorecard,
        recommendation_changed=current.target_analysis.is_recommended
        != baseline_report.target_analysis.is_recommended,
    )
    delta = DeltaReport(
        baseline_run_id=baseline.id,
        current_run_id=current.run_id,
        overall_delta=int(delta_payload["overall_delta"]),
        visibility_delta=int(delta_payload["visibility_delta"]),
        relevance_delta=int(delta_payload["relevance_delta"]),
        sentiment_delta=int(delta_payload["sentiment_delta"]),
        trust_delta=int(delta_payload["trust_delta"]),
        recommendation_changed=bool(delta_payload["recommendation_changed"]),
    )
    current_row = get_run_or_none(db, current.run_id)
    if current_row:
        current_row.delta_json = delta.model_dump(mode="json")
        db.add(current_row)
        db.commit()
    return RerunResponse(run=current, delta=delta)


@router.get("/runs/{run_id}", response_model=DiagnosticRunResponse)
async def get_run(run_id: str, db: Session = Depends(get_db)) -> DiagnosticRunResponse:
    """Return a persisted run by id."""
    row = get_run_or_none(db, run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    return DiagnosticRunResponse.model_validate(row.report_json)


@router.get("/reports/{run_id}/export")
async def export_run(
    run_id: str,
    format: str = Query(default="md", pattern="^(md|pdf)$"),
    db: Session = Depends(get_db),
) -> Response:
    """Export report to markdown or PDF."""
    row: DiagnosticRun | None = get_run_or_none(db, run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    report = DiagnosticRunResponse.model_validate(row.report_json)
    if format == "pdf":
        content = render_pdf(report)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=aeo-report-{run_id}.pdf"},
        )
    markdown = render_markdown(report)
    return Response(
        content=markdown.encode("utf-8"),
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=aeo-report-{run_id}.md"},
    )
