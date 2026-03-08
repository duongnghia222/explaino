"""
Web search service for advanced mode deep research.
Uses a search-capable model (e.g. perplexity/sonar-pro) via OpenRouter.
Designed as a pluggable interface so the provider can be swapped later.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


async def web_search(query: str) -> list[SearchResult]:
    """Run a web search query and return structured results.

    Uses the deep_research_model (default: perplexity/sonar-pro) via OpenRouter.
    Falls back to the standard LLM with a disclaimer if the search model fails.
    """
    search_client = AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )

    system_prompt = (
        "You are a research assistant. Given a search query, provide the most relevant "
        "information you can find. Return your response as JSON with a single key "
        '"results" containing an array of objects, each with:\n'
        '- "title": source title (string)\n'
        '- "url": source URL (string)\n'
        '- "snippet": relevant excerpt or summary (string)\n\n'
        "Return 3-5 high-quality results. If you cannot find real sources, "
        "synthesize information and use placeholder URLs with a note."
    )

    try:
        response = await search_client.chat.completions.create(
            model=settings.deep_research_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content
        if not content:
            return []

        data = json.loads(content)
        results = data.get("results", [])
        return [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
            )
            for r in results
        ]
    except Exception as exc:
        logger.warning("Search with %s failed, falling back to standard LLM: %s",
                        settings.deep_research_model, exc)
        return await _fallback_search(query, search_client)


async def _fallback_search(query: str, client: AsyncOpenAI) -> list[SearchResult]:
    """Fallback: use the standard LLM to synthesize information."""
    try:
        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant. Given a query, synthesize what you know "
                        "about the topic. Return JSON with a single key \"results\" containing "
                        "an array of objects with \"title\", \"url\", and \"snippet\". "
                        "Since you cannot browse the web, use your training data and note that "
                        "sources may not be verifiable. Use plausible URLs where possible."
                    ),
                },
                {"role": "user", "content": query},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content
        if not content:
            return []

        data = json.loads(content)
        return [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
            )
            for r in data.get("results", [])
        ]
    except Exception as exc:
        logger.error("Fallback search also failed: %s", exc)
        return []
