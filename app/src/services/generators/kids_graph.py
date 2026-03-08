"""Kids mode course generator — LangGraph implementation."""

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

from .state import KidsCourseState, report_progress

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a friendly teacher creating a fun storybook-style course for kids ages 5-10. "
    "Return your response as JSON with these keys:\n"
    '- "title": fun, exciting course title (string)\n'
    '- "description": brief exciting description (string)\n'
    '- "lessons": array of 4-6 lesson objects, each with:\n'
    '  - "title": fun lesson title (string)\n'
    '  - "text_blocks": array of 3-5 short text blocks (2-3 sentences each, simple language)\n'
    '  - "image_prompts": array of 2-3 objects with "prompt" (detailed image description for generation) and "alt_text" (short description)\n'
    '  - "key_points": array of 3 simple takeaways (strings)\n'
    '  - "quiz": array of 2 quiz question objects, each with:\n'
    '    - "question": simple question (string)\n'
    '    - "options": array of 3 answer options (strings, not 4)\n'
    '    - "correct_index": index of the correct option (0-2)\n'
    '    - "explanation": friendly explanation (string)\n\n'
    "Style: Use very simple words, short sentences, fun analogies, and emoji. "
    "Make it feel like a colorful storybook adventure! Each text block should be "
    "between images, like a picture book."
)


# ── Nodes ────────────────────────────────────────────────────────────────


async def plan_course(state: KidsCourseState) -> dict[str, Any]:
    await report_progress(state, "planning", "Creating a fun learning adventure...", 10)

    try:
        await report_progress(state, "generating", "Writing your storybook lessons...", 25)

        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Create a fun kids course about: {state['topic']}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
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


async def process_lesson(state: KidsCourseState) -> dict[str, Any]:
    """Process a single lesson: generate images, interleave with text blocks."""
    lesson_data: dict[str, Any] = state["_lesson_data"]  # type: ignore[typeddict-item]
    lesson_index: int = state["_lesson_index"]  # type: ignore[typeddict-item]

    text_blocks = lesson_data.get("text_blocks", [])
    image_prompts = lesson_data.get("image_prompts", [])

    images: list[ImageBlock] = []
    if image_prompts:
        images = await generate_images(image_prompts)

    # Interleave: text, image, text, image, text...
    content_blocks: list[ContentBlock] = []
    img_idx = 0
    for text in text_blocks:
        content_blocks.append(ContentBlock(type="text", text=text))
        if img_idx < len(images):
            content_blocks.append(ContentBlock(type="image", image=images[img_idx]))
            img_idx += 1

    # Append remaining images
    while img_idx < len(images):
        content_blocks.append(ContentBlock(type="image", image=images[img_idx]))
        img_idx += 1

    plain_content = "\n\n".join(text_blocks)

    entry = {
        "index": lesson_index,
        "title": lesson_data["title"],
        "content": plain_content,
        "content_blocks": [cb.model_dump() for cb in content_blocks],
        "citations": [],
        "key_points": lesson_data.get("key_points", []),
        "quiz": lesson_data.get("quiz", []),
    }
    return {"lesson_content_blocks": [entry]}


async def assemble_course(state: KidsCourseState) -> dict[str, Any]:
    await report_progress(state, "finishing", "Putting it all together!", 95)

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


def fan_out_lessons(state: KidsCourseState) -> list[Send]:
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

builder = StateGraph(KidsCourseState)
builder.add_node("plan_course", plan_course)
builder.add_node("process_lesson", process_lesson)
builder.add_node("assemble_course", assemble_course)

builder.add_edge(START, "plan_course")
builder.add_conditional_edges("plan_course", fan_out_lessons, ["process_lesson"])
builder.add_edge("process_lesson", "assemble_course")
builder.add_edge("assemble_course", END)

graph = builder.compile()


# ── Public API ───────────────────────────────────────────────────────────


async def generate_kids_course(topic: str, on_progress=None) -> dict:
    """Generate a kids-friendly course with image-heavy content."""
    result = await graph.ainvoke(
        {"topic": topic, "on_progress": on_progress},
    )
    return result["course_result"]
