"""Advanced mode course generator — LangGraph implementation."""

from __future__ import annotations

import logging
import re
from typing import Any
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from src.models.course import ContentBlock
from src.models.llm_responses import AdvancedCoursePlanResponse
from src.services.ai_client import AIServiceError, chat_model
from src.services.workflows.deep_research.deep_researcher import deep_researcher

from .state import AdvancedCourseState, report_progress

logger = logging.getLogger(__name__)


# ── Nodes ────────────────────────────────────────────────────────────────


async def deep_research(state: AdvancedCourseState) -> dict[str, Any]:
    """Run the deep research workflow and extract research context + sources."""
    await report_progress(state, "researching", "Running deep research...", 5)

    topic = state["topic"]
    result = await deep_researcher.ainvoke(
        {"messages": [HumanMessage(content=topic)]},
        config={},
    )

    final_report: str = result.get("final_report", "")

    await report_progress(state, "researching", "Processing research results...", 40)

    # Parse sources from the report's Sources/References section
    source_index: list[dict[str, Any]] = []
    sources_pattern = re.compile(
        r"(?:^|\n)##?\s*(?:Sources|References)\s*\n(.*)",
        re.DOTALL | re.IGNORECASE,
    )
    sources_match = sources_pattern.search(final_report)
    if sources_match:
        sources_text = sources_match.group(1)
        # Match lines like: - [Title](url) or [N] Title - url or numbered/bulleted entries with URLs
        url_pattern = re.compile(
            r"(?:\[([^\]]*)\]\((https?://[^\)]+)\))"  # markdown link [title](url)
            r"|"
            r"(https?://\S+)",  # bare URL
        )
        for match in url_pattern.finditer(sources_text):
            idx = len(source_index) + 1
            if match.group(1) and match.group(2):
                title = match.group(1)
                url = match.group(2)
            else:
                url = match.group(3)
                title = url
            source_index.append({
                "index": idx,
                "title": title,
                "url": url,
                "snippet": "",
            })

    return {
        "source_index": source_index,
        "research_context": final_report,
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


# ── Graph ────────────────────────────────────────────────────────────────

builder = StateGraph(AdvancedCourseState)
builder.add_node("deep_research", deep_research)
builder.add_node("synthesize_course", synthesize_course)
builder.add_node("assemble_course", assemble_course)

builder.add_edge(START, "deep_research")
builder.add_edge("deep_research", "synthesize_course")
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
