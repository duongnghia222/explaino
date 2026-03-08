"""Normal mode course generator — LangGraph implementation."""

from __future__ import annotations

import json
import logging
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from openai import OpenAIError

from src.config import settings
from src.models.course import ContentBlock, ImageBlock
from src.services.ai_client import AIServiceError, client
from src.services.image_service import generate_images

from .state import NormalCourseState, report_progress

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert course creator. Generate a structured course on the "
    "given topic. Return your response as JSON with these keys:\n"
    '- "title": course title (string)\n'
    '- "description": brief course description (string)\n'
    '- "lessons": array of 4-6 lesson objects, each with:\n'
    '  - "title": lesson title (string)\n'
    '  - "content": detailed lesson content in markdown (string)\n'
    '  - "image_prompts": array of 0-2 objects with "prompt" (description for diagram/illustration) and "alt_text" (short description). Only include if a visual would genuinely help understanding.\n'
    '  - "key_points": array of 3-5 key takeaways (strings)\n'
    '  - "quiz": array of 2-3 quiz question objects, each with:\n'
    '    - "question": the question (string)\n'
    '    - "options": array of 4 answer options (strings)\n'
    '    - "correct_index": index of the correct option (0-3)\n'
    '    - "explanation": why the correct answer is right (string)\n\n'
    "Style: Clear, standard language suitable for a general adult audience. "
    "Balance depth with accessibility. University-level educational content."
)


# ── Nodes ────────────────────────────────────────────────────────────────


async def plan_course(state: NormalCourseState) -> dict[str, Any]:
    await report_progress(state, "planning", "Planning your course...", 10)

    try:
        await report_progress(state, "generating", "Writing course content...", 25)

        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Create a course about: {state['topic']}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
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
