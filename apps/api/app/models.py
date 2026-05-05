"""SQLAlchemy models for diagnostic runs and provider responses."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


class DiagnosticRun(Base):
    """Persisted diagnostic run output and score."""

    __tablename__ = "diagnostic_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    target_url: Mapped[str] = mapped_column(Text)
    query: Mapped[str] = mapped_column(Text)
    competitor_mode: Mapped[str] = mapped_column(String(16))
    competitor_urls: Mapped[list[str]] = mapped_column(JSON)
    baseline_run_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_demo: Mapped[bool] = mapped_column(default=False)
    report_json: Mapped[dict] = mapped_column(JSON)
    score_json: Mapped[dict] = mapped_column(JSON)
    delta_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    provider_responses: Mapped[list["ProviderResponse"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class ProviderResponse(Base):
    """Persisted provider-level completion output and status metadata."""

    __tablename__ = "provider_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("diagnostic_runs.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(64))
    latency_ms: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16))
    output_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    run: Mapped[DiagnosticRun] = relationship(back_populates="provider_responses")

