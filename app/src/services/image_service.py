"""
Image generation service.
Uses OpenRouter image model if configured, otherwise returns placeholders.
"""

from __future__ import annotations

import asyncio
import logging
from uuid import uuid4

from src.config import settings
from src.models.course import ImageBlock
from src.services.ai_client import client

logger = logging.getLogger(__name__)


async def generate_image(prompt: str, alt_text: str = "") -> ImageBlock:
    """Generate a single image from a prompt.

    Falls back to a placeholder if no image model is configured or generation fails.
    """
    block_id = str(uuid4())

    if not settings.openrouter_image_model:
        return ImageBlock(
            id=block_id,
            url=None,
            alt_text=alt_text or prompt,
            prompt=prompt,
            placeholder=True,
        )

    try:
        response = await client.images.generate(
            model=settings.openrouter_image_model,
            prompt=prompt,
            n=1,
            size="1024x1024",
        )
        url = response.data[0].url if response.data else None
        return ImageBlock(
            id=block_id,
            url=url,
            alt_text=alt_text or prompt,
            prompt=prompt,
            placeholder=url is None,
        )
    except Exception as exc:
        logger.warning("Image generation failed, using placeholder: %s", exc)
        return ImageBlock(
            id=block_id,
            url=None,
            alt_text=alt_text or prompt,
            prompt=prompt,
            placeholder=True,
        )


async def generate_images(
    prompts: list[dict[str, str]],
) -> list[ImageBlock]:
    """Generate multiple images concurrently.

    Each item in *prompts* should have keys "prompt" and optionally "alt_text".
    """
    tasks = [
        generate_image(p["prompt"], p.get("alt_text", ""))
        for p in prompts
    ]
    return await asyncio.gather(*tasks)
