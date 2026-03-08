"""
AI Service for Course Generation
Dispatches to mode-specific generators.
"""

from __future__ import annotations

import logging
from typing import Callable, Awaitable

from src.services.generators.kids_graph import generate_kids_course
from src.services.generators.normal_graph import generate_normal_course
from src.services.generators.advanced_graph import generate_advanced_course

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, str, int], Awaitable[None]] | None

_generators: dict[str, Callable] = {
    "kids": generate_kids_course,
    "normal": generate_normal_course,
    "advanced": generate_advanced_course,
}


async def generate_course(
    topic: str,
    mode: str,
    on_progress: ProgressCallback = None,
) -> dict:
    """Generate a structured course on the given topic.

    Dispatches to the appropriate mode-specific generator.
    """
    generator = _generators.get(mode, generate_normal_course)
    return await generator(topic, on_progress=on_progress)
