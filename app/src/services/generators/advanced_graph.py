"""Advanced mode course generator — LangGraph implementation."""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from src.models.course import ContentBlock
from src.models.llm_responses import AdvancedCoursePlanResponse, ResearchPlanResponse
from src.services.ai_client import AIServiceError, chat_model
from src.services.search_service import web_search

from .state import AdvancedCourseState, report_progress

logger = logging.getLogger(__name__)


# ── Nodes ────────────────────────────────────────────────────────────────


async def generate_research_plan(state: AdvancedCourseState) -> dict[str, Any]:
    await report_progress(state, "planning", "Creating research plan...", 5)

    system_prompt = (
        "You are a research planner. Given a topic, generate 4-6 specific search queries "
        "that would help create a comprehensive, expert-level course. Respond in JSON format.\n\n"
        "Make queries specific and varied - cover fundamentals, recent developments, "
        "key debates, practical applications, and advanced concepts."
    )

    try:
        structured = chat_model.with_structured_output(
            ResearchPlanResponse, method="json_mode"
        )
        result = await structured.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Generate research queries for a course about: {state['topic']}"),
            ],
            config={"configurable": {"temperature": 0.5}},
        )

        queries = result.queries if result.queries else [state["topic"]]

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
        "You have access to research sources numbered [1], [2], etc. "
        "Respond in JSON format matching this EXACT schema:\n\n"
        '{"title": "...", "description": "...", "lessons": [{"title": "...", '
        '"content": "detailed markdown with [N] citations...", '
        '"cited_sources": [1, 2], '
        '"key_points": ["..."], '
        '"quiz": [{"question": "...", "options": ["A","B","C","D"], "correct_index": 0, "explanation": "..."}]'
        "}]}\n\n"
        "Style: Expert-level, research-backed, dense content with proper citations. "
        "Use technical terminology. Include nuanced analysis and multiple perspectives. "
        "Reference sources inline using [N] notation.\n\n"
        "Generate 4-6 lessons. Each lesson should have detailed expert-level markdown content "
        "with inline citations, a list of cited source numbers, 3-5 key takeaways, "
        "and 2-3 challenging quiz questions with 4 options each.\n\n"
        "IMPORTANT: Use exactly the field names shown above (title, content, key_points, quiz, etc.)."
    )

    try:
        structured = chat_model.with_structured_output(
            AdvancedCoursePlanResponse, method="json_mode"
        )
        result = await structured.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=(
                        f"Create an expert-level course about: {state['topic']}\n\n"
                        f"## Research Sources\n{state['research_context']}"
                    ),
                ),
            ],
            config={"configurable": {"temperature": 0.5}},
        )

        return {"raw_data": result.model_dump()}

    except Exception as exc:
        logger.error("Course synthesis failed: %s", exc)
        raise AIServiceError(f"Course synthesis failed: {exc}") from exc


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
