"""
Advanced mode course generator.
Multi-step deep research workflow with citations.
"""

from __future__ import annotations

import asyncio
import json
import logging
from uuid import uuid4

from openai import OpenAIError

from src.config import settings
from src.models.course import Citation, ContentBlock
from src.services.ai_client import AIServiceError, client
from src.services.search_service import SearchResult, web_search

logger = logging.getLogger(__name__)


async def generate_advanced_course(topic: str, on_progress=None) -> dict:
    """Generate an expert-level course with deep research and citations."""
    if on_progress:
        await on_progress("planning", "Creating research plan...", 5)

    # Step 1: Generate research plan
    research_queries = await _generate_research_plan(topic)

    if on_progress:
        await on_progress("researching", "Searching for sources...", 15)

    # Step 2: Web search for each query concurrently
    all_results: dict[str, list[SearchResult]] = {}
    search_tasks = {q: web_search(q) for q in research_queries}
    results_list = await asyncio.gather(*search_tasks.values())
    for query, results in zip(search_tasks.keys(), results_list):
        all_results[query] = results

    if on_progress:
        total_sources = sum(len(r) for r in all_results.values())
        await on_progress("researching", f"Found {total_sources} sources. Analyzing...", 40)

    # Step 3: Synthesize into course with citations
    if on_progress:
        await on_progress("synthesizing", "Writing expert-level lessons with citations...", 55)

    course_data = await _synthesize_course(topic, all_results)

    if on_progress:
        await on_progress("finishing", "Finalizing course...", 95)

    return course_data


async def _generate_research_plan(topic: str) -> list[str]:
    """Ask the LLM to generate search queries for thorough research."""
    system_prompt = (
        "You are a research planner. Given a topic, generate 4-6 specific search queries "
        "that would help create a comprehensive, expert-level course. Return JSON with a "
        'single key "queries" containing an array of search query strings.\n\n'
        "Make queries specific and varied - cover fundamentals, recent developments, "
        "key debates, practical applications, and advanced concepts."
    )

    try:
        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate research queries for a course about: {topic}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
        )

        content = response.choices[0].message.content
        if not content:
            return [topic]

        data = json.loads(content)
        queries = data.get("queries", [topic])
        return queries if queries else [topic]

    except Exception as exc:
        logger.warning("Research plan generation failed: %s", exc)
        return [topic, f"{topic} recent developments", f"{topic} expert analysis"]


async def _synthesize_course(
    topic: str, research: dict[str, list[SearchResult]]
) -> dict:
    """Synthesize research results into a structured course with citations."""
    # Build research context
    source_index: list[dict] = []
    research_text_parts: list[str] = []

    for query, results in research.items():
        research_text_parts.append(f"\n### Research for: {query}")
        for r in results:
            idx = len(source_index) + 1
            source_index.append({
                "index": idx,
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
            })
            research_text_parts.append(
                f"[{idx}] {r.title} ({r.url})\n{r.snippet}"
            )

    research_context = "\n".join(research_text_parts)

    system_prompt = (
        "You are an expert course creator synthesizing research into a comprehensive course. "
        "You have access to research sources numbered [1], [2], etc.\n\n"
        "Return your response as JSON with these keys:\n"
        '- "title": authoritative course title (string)\n'
        '- "description": expert-level course description (string)\n'
        '- "lessons": array of 4-6 lesson objects, each with:\n'
        '  - "title": precise lesson title (string)\n'
        '  - "content": detailed expert-level content in markdown with inline citations like [1], [2] (string)\n'
        '  - "cited_sources": array of source index numbers used in this lesson (integers)\n'
        '  - "key_points": array of 3-5 key takeaways (strings)\n'
        '  - "quiz": array of 2-3 quiz question objects, each with:\n'
        '    - "question": challenging expert-level question (string)\n'
        '    - "options": array of 4 answer options (strings)\n'
        '    - "correct_index": index of the correct option (0-3)\n'
        '    - "explanation": detailed explanation with source references (string)\n\n'
        "Style: Expert-level, research-backed, dense content with proper citations. "
        "Use technical terminology. Include nuanced analysis and multiple perspectives. "
        "Reference sources inline using [N] notation."
    )

    try:
        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Create an expert-level course about: {topic}\n\n"
                        f"## Research Sources\n{research_context}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
        )

        content = response.choices[0].message.content
        if content is None:
            raise AIServiceError("Empty response from AI")

        data = json.loads(content)

        if "title" not in data or "lessons" not in data:
            raise AIServiceError("Missing required fields in AI response")

        # Build lessons with citations
        lessons = []
        for lesson_data in data["lessons"]:
            cited_indices = lesson_data.get("cited_sources", [])
            citations = []
            for idx in cited_indices:
                if 1 <= idx <= len(source_index):
                    src = source_index[idx - 1]
                    citations.append({
                        "id": str(uuid4()),
                        "title": src["title"],
                        "url": src["url"],
                        "snippet": src["snippet"],
                    })

            content_blocks = [
                ContentBlock(type="text", text=lesson_data["content"]).model_dump()
            ]

            lessons.append({
                "title": lesson_data["title"],
                "content": lesson_data["content"],
                "content_blocks": content_blocks,
                "citations": citations,
                "key_points": lesson_data.get("key_points", []),
                "quiz": lesson_data.get("quiz", []),
            })

        return {
            "title": data["title"],
            "description": data.get("description", ""),
            "lessons": lessons,
        }

    except OpenAIError as exc:
        logger.error("OpenRouter API error: %s", exc)
        raise AIServiceError(f"OpenRouter API error: {exc}") from exc
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI response: %s", exc)
        raise AIServiceError("Invalid JSON in AI response") from exc
