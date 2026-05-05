"""Competitor discovery service with paid-primary and free fallback paths."""

from __future__ import annotations

from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup  # type: ignore[import-untyped]

from app.core.config import Settings


class CompetitorDiscoveryService:
    """Resolve competitor product URLs from search sources."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def discover(self, query: str, limit: int = 5) -> list[str]:
        """Discover competitor URLs using SerpAPI first and fallback to free search."""
        if self._settings.serpapi_key:
            urls = await self._discover_via_serpapi(query, limit)
            if urls:
                return urls[:limit]
        urls = await self._discover_via_free_search(query, limit)
        return urls[:limit]

    async def _discover_via_serpapi(self, query: str, limit: int) -> list[str]:
        endpoint = "https://serpapi.com/search.json"
        params = {
            "engine": "amazon",
            "k": query,
            "api_key": self._settings.serpapi_key,
        }
        timeout = self._settings.http_timeout_seconds
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
        products = data.get("organic_results", [])
        urls = []
        for item in products:
            link = item.get("link")
            if isinstance(link, str) and "amazon." in link:
                urls.append(_normalize_amazon_url(link))
        return list(dict.fromkeys(urls))[:limit]

    async def _discover_via_free_search(self, query: str, limit: int) -> list[str]:
        search_query = quote(f"site:amazon.com {query}")
        endpoint = f"https://duckduckgo.com/html/?q={search_query}"
        timeout = self._settings.http_timeout_seconds
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(endpoint)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        urls: list[str] = []
        for anchor in soup.select("a.result__a"):
            href = anchor.get("href", "")
            if "amazon." in href:
                urls.append(_normalize_amazon_url(href))
            if len(urls) >= limit:
                break
        return list(dict.fromkeys(urls))[:limit]


def _normalize_amazon_url(url: str) -> str:
    """Normalize Amazon URL for stable comparison across runs."""
    clean = url.split("?")[0]
    clean = clean.replace("smile.amazon.", "www.amazon.")
    return clean
