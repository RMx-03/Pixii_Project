"""Provider clients for OpenAI, Anthropic, and Gemini."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings
from app.services.normalization import extract_json_object, normalize_provider_output


@dataclass
class ProviderResult:
    """Structured provider call result with status metadata."""

    provider: str
    model: str
    status: str
    latency_ms: int
    output: dict[str, Any] | None
    error: str | None


class ProviderClient:
    """Unified provider calling interface."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def run_openai(self, prompt: str) -> ProviderResult:
        """Run OpenAI request with JSON-only output instruction."""
        if not self._settings.openai_api_key:
            return ProviderResult(
                provider="openai",
                model=self._settings.openai_model,
                status="skipped",
                latency_ms=0,
                output=None,
                error="OPENAI_API_KEY is missing",
            )
        url = "https://api.openai.com/v1/responses"
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._settings.openai_model,
            "input": prompt,
            "temperature": 0.2,
        }
        return await self._execute("openai", self._settings.openai_model, url, headers, payload)

    async def run_anthropic(self, prompt: str) -> ProviderResult:
        """Run Anthropic request with JSON-only output instruction."""
        if not self._settings.anthropic_api_key:
            return ProviderResult(
                provider="anthropic",
                model=self._settings.anthropic_model,
                status="skipped",
                latency_ms=0,
                output=None,
                error="ANTHROPIC_API_KEY is missing",
            )
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self._settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._settings.anthropic_model,
            "max_tokens": 1600,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }
        return await self._execute("anthropic", self._settings.anthropic_model, url, headers, payload)

    async def run_gemini(self, prompt: str) -> ProviderResult:
        """Run Gemini request with JSON-only output instruction."""
        if not self._settings.gemini_api_key:
            return ProviderResult(
                provider="gemini",
                model=self._settings.gemini_model,
                status="skipped",
                latency_ms=0,
                output=None,
                error="GEMINI_API_KEY is missing",
            )
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._settings.gemini_model}:generateContent?key={self._settings.gemini_api_key}"
        )
        headers = {"Content-Type": "application/json"}
        payload = {
            "generationConfig": {"temperature": 0.2},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        }
        return await self._execute("gemini", self._settings.gemini_model, url, headers, payload)

    async def _execute(
        self, provider: str, model: str, url: str, headers: dict[str, str], payload: dict[str, Any]
    ) -> ProviderResult:
        started = time.perf_counter()
        timeout = self._settings.http_timeout_seconds
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            text = _extract_text(provider, data)
            parsed = extract_json_object(text)
            normalized = normalize_provider_output(parsed).model_dump(mode="json")
            elapsed = int((time.perf_counter() - started) * 1000)
            return ProviderResult(
                provider=provider,
                model=model,
                status="ok",
                latency_ms=elapsed,
                output=normalized,
                error=None,
            )
        except Exception as exc:
            elapsed = int((time.perf_counter() - started) * 1000)
            return ProviderResult(
                provider=provider,
                model=model,
                status="error",
                latency_ms=elapsed,
                output=None,
                error=str(exc),
            )


def _extract_text(provider: str, data: dict[str, Any]) -> str:
    """Extract textual answer from provider-specific payload."""
    if provider == "openai":
        content = data.get("output", [])
        for item in content:
            item_content = item.get("content", [])
            for block in item_content:
                text = block.get("text")
                if isinstance(text, str):
                    return text
        output_text = data.get("output_text")
        if isinstance(output_text, str):
            return output_text
    if provider == "anthropic":
        blocks = data.get("content", [])
        for block in blocks:
            text = block.get("text")
            if isinstance(text, str):
                return text
    if provider == "gemini":
        candidates = data.get("candidates", [])
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                text = part.get("text")
                if isinstance(text, str):
                    return text
    raise ValueError(f"Unable to parse text from {provider} response")
