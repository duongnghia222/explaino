"""Shared state types and helpers for LangGraph course generators."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Callable, Awaitable, TypedDict


ProgressCallback = Callable[[str, str, int], Awaitable[None]] | None


async def report_progress(
    state: dict[str, Any],
    stage: str,
    message: str,
    percent: int,
) -> None:
    """Fire a progress callback if one exists in state."""
    cb = state.get("on_progress")
    if cb:
        await cb(stage, message, percent)


class BaseCourseState(TypedDict, total=False):
    topic: str
    on_progress: ProgressCallback
    raw_data: dict[str, Any]
    course_result: dict[str, Any]


class KidsCourseState(BaseCourseState, total=False):
    lesson_content_blocks: Annotated[list, operator.add]


class NormalCourseState(BaseCourseState, total=False):
    lesson_content_blocks: Annotated[list, operator.add]


class AdvancedCourseState(BaseCourseState, total=False):
    source_index: list[dict[str, Any]]
    research_context: str
