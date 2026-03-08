"""
Course API Routes
Endpoints for course generation and retrieval
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from src.models.course import (
    Citation,
    ContentBlock,
    CourseRecord,
    CourseRequest,
    CourseResponse,
    ImageBlock,
    Lesson,
    LessonResponse,
    QuizQuestion,
)
from src.services.course_service import generate_course
from src.services.course_storage import get_all_courses, get_course, save_course

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/courses", tags=["courses"])


def _build_record(request: CourseRequest, result: dict) -> CourseRecord:
    """Build a CourseRecord from the raw generator result."""
    lessons = []
    for lesson_data in result["lessons"]:
        quiz_questions = []
        for q in lesson_data.get("quiz", []):
            quiz_questions.append(
                QuizQuestion(
                    id=str(uuid4()),
                    question=q["question"],
                    options=q["options"],
                    correct_index=q["correct_index"],
                    explanation=q["explanation"],
                )
            )

        content_blocks = []
        for cb in lesson_data.get("content_blocks", []):
            if isinstance(cb, dict):
                content_blocks.append(ContentBlock(**cb))
            elif isinstance(cb, ContentBlock):
                content_blocks.append(cb)

        citations = []
        for c in lesson_data.get("citations", []):
            if isinstance(c, dict):
                citations.append(Citation(**c))
            elif isinstance(c, Citation):
                citations.append(c)

        lessons.append(
            Lesson(
                id=str(uuid4()),
                title=lesson_data["title"],
                content=lesson_data.get("content", ""),
                content_blocks=content_blocks,
                citations=citations,
                key_points=lesson_data.get("key_points", []),
                quiz=quiz_questions,
            )
        )

    return CourseRecord(
        id=str(uuid4()),
        topic=request.topic,
        mode=request.mode,
        title=result["title"],
        description=result.get("description", ""),
        lessons=lessons,
        created_at=datetime.now(timezone.utc),
    )


@router.post("", response_model=CourseResponse)
async def create_course(request: CourseRequest) -> CourseResponse:
    """Generate a new course on the given topic (non-streaming)."""
    result = await generate_course(topic=request.topic, mode=request.mode.value)
    record = _build_record(request, result)
    save_course(record)
    return CourseResponse(**record.model_dump())


@router.get("", response_model=list[CourseResponse])
async def list_courses() -> list[CourseResponse]:
    """List all courses."""
    courses = get_all_courses()
    return [CourseResponse(**c.model_dump()) for c in courses]


@router.get("/{id}", response_model=CourseResponse)
async def get_course_by_id(id: str) -> CourseResponse:
    """Retrieve a specific course by ID."""
    record = get_course(id)
    if record is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return CourseResponse(**record.model_dump())


@router.get("/{id}/lessons/{lesson_id}", response_model=LessonResponse)
async def get_lesson(id: str, lesson_id: str) -> LessonResponse:
    """Retrieve a specific lesson from a course."""
    record = get_course(id)
    if record is None:
        raise HTTPException(status_code=404, detail="Course not found")

    for lesson in record.lessons:
        if lesson.id == lesson_id:
            return LessonResponse(**lesson.model_dump())

    raise HTTPException(status_code=404, detail="Lesson not found")
