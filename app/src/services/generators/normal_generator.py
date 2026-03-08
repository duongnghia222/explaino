"""
Normal mode course generator.
Produces clear educational content with occasional illustrations.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import uuid4

from openai import OpenAIError

from src.config import settings
from src.models.course import ContentBlock, ImageBlock
from src.services.ai_client import AIServiceError, client
from src.services.image_service import generate_images

logger = logging.getLogger(__name__)


async def generate_normal_course(topic: str, on_progress=None) -> dict:
    """Generate a standard educational course with optional diagrams."""
    if on_progress:
        await on_progress("planning", "Planning your course...", 10)

    system_prompt = (
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

    try:
        if on_progress:
            await on_progress("generating", "Writing course content...", 25)

        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a course about: {topic}"},
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

        if on_progress:
            await on_progress("images", "Generating illustrations...", 55)

        lessons = []
        for i, lesson_data in enumerate(data["lessons"]):
            if on_progress:
                pct = 55 + int((i / len(data["lessons"])) * 35)
                await on_progress("images", f"Processing lesson {i + 1}...", pct)

            content_blocks = await _build_normal_content_blocks(lesson_data)

            lessons.append({
                "title": lesson_data["title"],
                "content": lesson_data["content"],
                "content_blocks": [cb.model_dump() for cb in content_blocks],
                "citations": [],
                "key_points": lesson_data.get("key_points", []),
                "quiz": lesson_data.get("quiz", []),
            })

        if on_progress:
            await on_progress("finishing", "Finalizing course...", 95)

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


async def _build_normal_content_blocks(lesson_data: dict[str, Any]) -> list[ContentBlock]:
    """Build content blocks with text and optional images."""
    image_prompts = lesson_data.get("image_prompts", [])

    # Generate images if any prompts exist
    images: list[ImageBlock] = []
    if image_prompts:
        images = await generate_images(image_prompts)

    # Main content as text block, with images appended after
    content_blocks: list[ContentBlock] = [
        ContentBlock(type="text", text=lesson_data["content"])
    ]

    for img in images:
        content_blocks.append(ContentBlock(type="image", image=img))

    return content_blocks
