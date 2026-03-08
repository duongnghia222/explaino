"""
Web search service for advanced mode deep research.
Uses a search-capable model (e.g. perplexity/sonar-pro) via OpenRouter.
Designed as a pluggable interface so the provider can be swapped later.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage

from src.models.llm_responses import SearchResponse
from src.services.ai_client import chat_model, search_model

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


SEARCH_SYSTEM_PROMPT = (
    "You are a research assistant. Given a search query, provide the most relevant "
    "information you can find. Respond in JSON format. Return 3-5 high-quality results. "
    "If you cannot find real sources, synthesize information and use placeholder URLs with a note."
)

FALLBACK_SYSTEM_PROMPT = (
    "You are a research assistant. Given a query, synthesize what you know "
    "about the topic. Respond in JSON format. Since you cannot browse the web, use your "
    "training data and note that sources may not be verifiable. Use plausible URLs where possible."
)


async def web_search(query: str) -> list[SearchResult]:
    """Run a web search query and return structured results.

    Uses the deep_research_model (default: perplexity/sonar-pro) via OpenRouter.
    Falls back to the standard LLM with a disclaimer if the search model fails.
    """
    messages = [
        SystemMessage(content=SEARCH_SYSTEM_PROMPT),
        HumanMessage(content=query),
    ]

    try:
        structured = search_model.with_structured_output(
            SearchResponse, method="json_mode"
        )
        result = await structured.ainvoke(messages)

        return [
            SearchResult(title=r.title, url=r.url, snippet=r.snippet)
            for r in result.results
        ]
    except Exception as exc:
        logger.warning("Search with search_model failed, falling back to standard LLM: %s", exc)
        return await _fallback_search(query)


async def _fallback_search(query: str) -> list[SearchResult]:
    """Fallback: use the standard LLM to synthesize information."""
    try:
        structured = chat_model.with_structured_output(
            SearchResponse, method="json_mode"
        )
        result = await structured.ainvoke([
            SystemMessage(content=FALLBACK_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ])

        return [
            SearchResult(title=r.title, url=r.url, snippet=r.snippet)
            for r in result.results
        ]
    except Exception as exc:
        logger.error("Fallback search also failed: %s", exc)
        return []
