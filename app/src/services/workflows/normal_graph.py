"""Normal mode course generator — LangGraph implementation."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from src.models.course import ContentBlock, ImageBlock
from src.models.llm_responses import NormalCoursePlanResponse
from src.services.ai_client import AIServiceError, chat_model
from src.services.image_service import generate_images

from .state import NormalCourseState, report_progress

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert course creator. Generate a structured course on the "
    "given topic. Respond in JSON format matching this EXACT schema:\n\n"
    '{"title": "...", "description": "...", "lessons": [{"title": "...", '
    '"content": "detailed markdown...", '
    '"image_prompts": [{"prompt": "...", "alt_text": "..."}], '
    '"key_points": ["..."], '
    '"quiz": [{"question": "...", "options": ["A","B","C","D"], "correct_index": 0, "explanation": "..."}]'
    "}]}\n\n"
    "Style: Clear, standard language suitable for a general adult audience. "
    "Balance depth with accessibility. University-level educational content.\n\n"
    "Generate 4-6 lessons. Each lesson should have detailed markdown content, "
    "0-2 image prompts (only if a visual would genuinely help understanding), "
    "3-5 key takeaways, and 2-3 quiz questions with 4 options each.\n\n"
    "IMPORTANT: Use exactly the field names shown above (title, content, key_points, quiz, etc.)."
)


# ── Nodes ────────────────────────────────────────────────────────────────


async def plan_course(state: NormalCourseState) -> dict[str, Any]:
    await report_progress(state, "planning", "Planning your course...", 10)

    try:
        await report_progress(state, "generating", "Writing course content...", 25)

        structured = chat_model.with_structured_output(
            NormalCoursePlanResponse, method="json_mode"
        )
        result = await structured.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"Create a course about: {state['topic']}"),
            ],
            config={"configurable": {"temperature": 0.7}},
        )

        return {"raw_data": result.model_dump()}

    except Exception as exc:
        logger.error("Course planning failed: %s", exc)
        raise AIServiceError(f"Course planning failed: {exc}") from exc


async def process_lesson(state: NormalCourseState) -> dict[str, Any]:
    """Process a single lesson: generate images, build content blocks."""
    lesson_data: dict[str, Any] = state["_lesson_data"]  # type: ignore[typeddict-item]
    lesson_index: int = state["_lesson_index"]  # type: ignore[typeddict-item]

    image_prompts = lesson_data.get("image_prompts", [])
    images: list[ImageBlock] = []
    if image_prompts:
        images = await generate_images(image_prompts)

    content_blocks: list[ContentBlock] = [
        ContentBlock(type="text", text=lesson_data["content"])
    ]
    for img in images:
        content_blocks.append(ContentBlock(type="image", image=img))

    entry = {
        "index": lesson_index,
        "title": lesson_data["title"],
        "content": lesson_data["content"],
        "content_blocks": [cb.model_dump() for cb in content_blocks],
        "citations": [],
        "key_points": lesson_data.get("key_points", []),
        "quiz": lesson_data.get("quiz", []),
    }
    return {"lesson_content_blocks": [entry]}


async def assemble_course(state: NormalCourseState) -> dict[str, Any]:
    await report_progress(state, "finishing", "Finalizing course...", 95)

    blocks = sorted(state["lesson_content_blocks"], key=lambda b: b["index"])
    lessons = [
        {k: v for k, v in block.items() if k != "index"} for block in blocks
    ]

    return {
        "course_result": {
            "title": state["raw_data"]["title"],
            "description": state["raw_data"].get("description", ""),
            "lessons": lessons,
        }
    }


# ── Conditional edge ─────────────────────────────────────────────────────


def fan_out_lessons(state: NormalCourseState) -> list[Send]:
    data = state["raw_data"]
    sends = []
    for i, lesson_data in enumerate(data["lessons"]):
        sends.append(
            Send(
                "process_lesson",
                {
                    **state,
                    "_lesson_data": lesson_data,
                    "_lesson_index": i,
                },
            )
        )
    return sends


# ── Graph ────────────────────────────────────────────────────────────────

builder = StateGraph(NormalCourseState)
builder.add_node("plan_course", plan_course)
builder.add_node("process_lesson", process_lesson)
builder.add_node("assemble_course", assemble_course)

builder.add_edge(START, "plan_course")
builder.add_conditional_edges("plan_course", fan_out_lessons, ["process_lesson"])
builder.add_edge("process_lesson", "assemble_course")
builder.add_edge("assemble_course", END)

graph = builder.compile()


# ── Public API ───────────────────────────────────────────────────────────


async def generate_normal_course(topic: str, on_progress=None) -> dict:
    """Generate a standard educational course with optional diagrams."""
    result = await graph.ainvoke(
        {"topic": topic, "on_progress": on_progress},
    )
    return result["course_result"]
