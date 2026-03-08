"""
Course Data Models
Pydantic models for course generation requests and responses
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class CourseMode(str, Enum):
    kids = "kids"
    normal = "normal"
    advanced = "advanced"


class CourseRequest(BaseModel):
    topic: str
    mode: CourseMode


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class Lesson(BaseModel):
    id: str
    title: str
    content: str
    key_points: list[str]
    quiz: list[QuizQuestion]


class CourseRecord(BaseModel):
    id: str
    topic: str
    mode: CourseMode
    title: str
    description: str
    lessons: list[Lesson]
    created_at: datetime


class CourseResponse(BaseModel):
    id: str
    topic: str
    mode: CourseMode
    title: str
    description: str
    lessons: list[Lesson]
    created_at: datetime


class LessonResponse(BaseModel):
    id: str
    title: str
    content: str
    key_points: list[str]
    quiz: list[QuizQuestion]
