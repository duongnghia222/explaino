"""Advanced mode course generator — LangGraph implementation."""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from openai import OpenAIError

from src.config import settings
from src.models.course import ContentBlock
from src.services.ai_client import AIServiceError, client
from src.services.search_service import web_search

from .state import AdvancedCourseState, report_progress

logger = logging.getLogger(__name__)


# ── Nodes ────────────────────────────────────────────────────────────────


async def generate_research_plan(state: AdvancedCourseState) -> dict[str, Any]:
    await report_progress(state, "planning", "Creating research plan...", 5)

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
                {"role": "user", "content": f"Generate research queries for a course about: {state['topic']}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
        )

        content = response.choices[0].message.content
        if not content:
            return {"research_queries": [state["topic"]]}

        data = json.loads(content)
        queries = data.get("queries", [state["topic"]])
        if not queries:
            queries = [state["topic"]]

        await report_progress(state, "researching", "Searching for sources...", 15)
        return {"research_queries": queries}

    except Exception as exc:
        logger.warning("Research plan generation failed: %s", exc)
        topic = state["topic"]
        return {
            "research_queries": [
                topic,
                f"{topic} recent developments",
                f"{topic} expert analysis",
            ]
        }


async def execute_search(state: AdvancedCourseState) -> dict[str, Any]:
    """Execute a single web search query."""
    query: str = state["_query"]  # type: ignore[typeddict-item]
    results = await web_search(query)
    return {
        "search_results": [
            {
                "query": query,
                "results": [
                    {"title": r.title, "url": r.url, "snippet": r.snippet}
                    for r in results
                ],
            }
        ]
    }


async def build_context(state: AdvancedCourseState) -> dict[str, Any]:
    total_sources = sum(len(sr["results"]) for sr in state["search_results"])
    await report_progress(
        state, "researching", f"Found {total_sources} sources. Analyzing...", 40
    )

    source_index: list[dict[str, Any]] = []
    research_text_parts: list[str] = []

    for sr in state["search_results"]:
        research_text_parts.append(f"\n### Research for: {sr['query']}")
        for r in sr["results"]:
            idx = len(source_index) + 1
            source_index.append({
                "index": idx,
                "title": r["title"],
                "url": r["url"],
                "snippet": r["snippet"],
            })
            research_text_parts.append(
                f"[{idx}] {r['title']} ({r['url']})\n{r['snippet']}"
            )

    return {
        "source_index": source_index,
        "research_context": "\n".join(research_text_parts),
    }


async def synthesize_course(state: AdvancedCourseState) -> dict[str, Any]:
    await report_progress(
        state, "synthesizing", "Writing expert-level lessons with citations...", 55
    )

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
                        f"Create an expert-level course about: {state['topic']}\n\n"
                        f"## Research Sources\n{state['research_context']}"
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

        return {"raw_data": data}

    except OpenAIError as exc:
        logger.error("OpenRouter API error: %s", exc)
        raise AIServiceError(f"OpenRouter API error: {exc}") from exc
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI response: %s", exc)
        raise AIServiceError("Invalid JSON in AI response") from exc


async def assemble_course(state: AdvancedCourseState) -> dict[str, Any]:
    await report_progress(state, "finishing", "Finalizing course...", 95)

    source_index = state["source_index"]
    data = state["raw_data"]

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
        "course_result": {
            "title": data["title"],
            "description": data.get("description", ""),
            "lessons": lessons,
        }
    }


# ── Conditional edges ────────────────────────────────────────────────────


def fan_out_searches(state: AdvancedCourseState) -> list[Send]:
    return [
        Send("execute_search", {**state, "_query": q})
        for q in state["research_queries"]
    ]


# ── Graph ────────────────────────────────────────────────────────────────

builder = StateGraph(AdvancedCourseState)
builder.add_node("generate_research_plan", generate_research_plan)
builder.add_node("execute_search", execute_search)
builder.add_node("build_context", build_context)
builder.add_node("synthesize_course", synthesize_course)
builder.add_node("assemble_course", assemble_course)

builder.add_edge(START, "generate_research_plan")
builder.add_conditional_edges("generate_research_plan", fan_out_searches, ["execute_search"])
builder.add_edge("execute_search", "build_context")
builder.add_edge("build_context", "synthesize_course")
builder.add_edge("synthesize_course", "assemble_course")
builder.add_edge("assemble_course", END)

graph = builder.compile()


# ── Public API ───────────────────────────────────────────────────────────


async def generate_advanced_course(topic: str, on_progress=None) -> dict:
    """Generate an expert-level course with deep research and citations."""
    result = await graph.ainvoke(
        {"topic": topic, "on_progress": on_progress},
    )
    return result["course_result"]
