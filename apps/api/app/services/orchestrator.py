"""Diagnostic orchestration service for multi-provider AEO reporting."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Literal

from app.core.config import Settings
from app.models import ProviderResponse
from app.schemas import (
    DiagnosticRunResponse,
    ProviderOutput,
)
from app.services.demo_mode import build_demo_provider_outputs
from app.services.discovery import CompetitorDiscoveryService
from app.services.prompting import build_diagnostic_prompt
from app.services.providers import ProviderClient, ProviderResult
from app.services.scoring import analyze_target_recommendation, compute_scorecard, merge_action_plan


class DiagnosticOrchestrator:
    """Coordinate competitor discovery, provider calls, and report assembly."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider_client = ProviderClient(settings)
        self._discovery = CompetitorDiscoveryService(settings)

    async def run_diagnostic(
        self,
        target_url: str,
        query: str,
        competitor_mode: str,
        competitor_urls: list[str],
    ) -> tuple[DiagnosticRunResponse, list[ProviderResponse], dict]:
        """Build full diagnostic report with provider metadata rows."""
        resolved_competitors = (
            competitor_urls
            if competitor_mode == "manual" and competitor_urls
            else await self._discovery.discover(query, limit=5)
        )
        prompt = build_diagnostic_prompt(target_url, query, resolved_competitors)
        has_any_key = any(
            [
                self._settings.openai_api_key,
                self._settings.anthropic_api_key,
                self._settings.gemini_api_key,
            ]
        )
        warnings: list[str] = []
        mode: Literal["live", "demo"]
        if not has_any_key:
            providers = build_demo_provider_outputs(query=query, target_url=target_url)
            warnings.append("Demo mode active because no provider API keys were configured.")
            metadata_rows = _metadata_from_demo(providers)
            mode = "demo"
        else:
            results = await asyncio.gather(
                self._provider_client.run_openai(prompt),
                self._provider_client.run_anthropic(prompt),
                self._provider_client.run_gemini(prompt),
            )
            providers, metadata_rows, warnings = _convert_results(results)
            mode = "live"

        scorecard = compute_scorecard(providers, target_url=target_url)
        target_analysis = analyze_target_recommendation(providers, target_url=target_url)
        action_plan = merge_action_plan(providers)
        created_at = datetime.now(timezone.utc)

        response = DiagnosticRunResponse(
            run_id="",
            created_at=created_at,
            target_url=target_url,
            query=query,
            mode=mode,
            providers=providers,
            scorecard=scorecard,
            target_analysis=target_analysis,
            action_plan=action_plan,
            warnings=warnings,
            competitor_urls=resolved_competitors,
        )
        computed = {
            "scorecard": scorecard.model_dump(),
            "target_analysis": target_analysis.model_dump(),
        }
        return response, metadata_rows, computed


def _convert_results(
    results: Sequence[ProviderResult],
) -> tuple[list[ProviderOutput], list[ProviderResponse], list[str]]:
    providers: list[ProviderOutput] = []
    rows: list[ProviderResponse] = []
    warnings: list[str] = []
    for result in results:
        row = ProviderResponse(
            provider=result.provider,
            model=result.model,
            status=result.status,
            latency_ms=result.latency_ms,
            output_json=result.output,
            error_text=result.error,
        )
        rows.append(row)
        if result.status == "ok" and result.output:
            providers.append(ProviderOutput.model_validate(result.output))
        elif result.status == "skipped":
            warnings.append(f"{result.provider} skipped: {result.error}")
        else:
            warnings.append(f"{result.provider} failed: {result.error}")
    return providers, rows, warnings


def _metadata_from_demo(providers: list[ProviderOutput]) -> list[ProviderResponse]:
    rows: list[ProviderResponse] = []
    for provider in providers:
        rows.append(
            ProviderResponse(
                provider=provider.provider_name,
                model=provider.model,
                status="ok",
                latency_ms=0,
                output_json=provider.model_dump(mode="json"),
                error_text=None,
            )
        )
    return rows
