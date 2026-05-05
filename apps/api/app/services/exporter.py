"""Report export service for Markdown and PDF outputs."""

from __future__ import annotations

from io import BytesIO

from app.schemas import DiagnosticRunResponse


def render_markdown(report: DiagnosticRunResponse) -> str:
    """Render report into markdown content."""
    providers = "\n".join(
        f"- **{item.provider_name}** verdict: `{item.overall_verdict}`" for item in report.providers
    )
    evidence = "\n".join(
        f"- {snippet}"
        for provider in report.providers
        for snippet in provider.evidence_snippets[:2]
    )
    tasks = "\n".join(f"- {task}" for task in report.action_plan.priority_tasks)
    warnings = "\n".join(f"- {warning}" for warning in report.warnings) or "- none"
    return (
        f"# AEO Report Card\n\n"
        f"Run ID: `{report.run_id}`\n\n"
        f"Mode: `{report.mode}`\n\n"
        f"## Scorecard\n"
        f"- Overall: **{report.scorecard.overall}**\n"
        f"- Visibility: {report.scorecard.visibility}\n"
        f"- Relevance: {report.scorecard.relevance}\n"
        f"- Sentiment: {report.scorecard.sentiment}\n"
        f"- Trust: {report.scorecard.trust}\n\n"
        f"## Provider Verdicts\n{providers}\n\n"
        f"## Evidence Snippets\n{evidence}\n\n"
        f"## Priority Actions\n{tasks}\n\n"
        f"## Warnings\n{warnings}\n"
    )


def render_pdf(report: DiagnosticRunResponse) -> bytes:
    """Render report into PDF bytes."""
    from fpdf import FPDF

    markdown = render_markdown(report)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    for line in markdown.splitlines():
        pdf.multi_cell(0, 6, text=line)
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
