"""
Kids mode course generator.
Produces storybook-like content with high image-to-text ratio.
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


async def generate_kids_course(topic: str, on_progress=None) -> dict:
    """Generate a kids-friendly course with image-heavy content."""
    if on_progress:
        await on_progress("planning", "Creating a fun learning adventure...", 10)

    system_prompt = (
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

    try:
        if on_progress:
            await on_progress("generating", "Writing your storybook lessons...", 25)

        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a fun kids course about: {topic}"},
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

        if on_progress:
            await on_progress("images", "Creating pictures for your story...", 50)

        lessons = []
        for i, lesson_data in enumerate(data["lessons"]):
            if on_progress:
                pct = 50 + int((i / len(data["lessons"])) * 40)
                await on_progress("images", f"Drawing pictures for lesson {i + 1}...", pct)

            content_blocks = await _build_kids_content_blocks(lesson_data)

            # Build fallback plain content
            plain_content = "\n\n".join(lesson_data.get("text_blocks", []))

            lessons.append({
                "title": lesson_data["title"],
                "content": plain_content,
                "content_blocks": [cb.model_dump() for cb in content_blocks],
                "citations": [],
                "key_points": lesson_data.get("key_points", []),
                "quiz": lesson_data.get("quiz", []),
            })

        if on_progress:
            await on_progress("finishing", "Putting it all together!", 95)

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


async def _build_kids_content_blocks(lesson_data: dict[str, Any]) -> list[ContentBlock]:
    """Interleave text blocks with generated images."""
    text_blocks = lesson_data.get("text_blocks", [])
    image_prompts = lesson_data.get("image_prompts", [])

    # Generate all images concurrently
    images: list[ImageBlock] = []
    if image_prompts:
        images = await generate_images(image_prompts)

    # Interleave: text, image, text, image, text...
    content_blocks: list[ContentBlock] = []
    img_idx = 0

    for j, text in enumerate(text_blocks):
        content_blocks.append(ContentBlock(type="text", text=text))

        # Insert an image after each text block (if available)
        if img_idx < len(images):
            content_blocks.append(ContentBlock(type="image", image=images[img_idx]))
            img_idx += 1

    # Append any remaining images
    while img_idx < len(images):
        content_blocks.append(ContentBlock(type="image", image=images[img_idx]))
        img_idx += 1

    return content_blocks
