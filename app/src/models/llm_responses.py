"""Pydantic models for LLM structured output responses."""

from __future__ import annotations

from pydantic import BaseModel


# ── Shared ──────────────────────────────────────────────────────────────


class QuizQuestionResponse(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class ImagePromptResponse(BaseModel):
    prompt: str
    alt_text: str


# ── Normal mode ─────────────────────────────────────────────────────────


class NormalLessonResponse(BaseModel):
    title: str
    content: str
    image_prompts: list[ImagePromptResponse] = []
    key_points: list[str]
    quiz: list[QuizQuestionResponse]


class NormalCoursePlanResponse(BaseModel):
    title: str
    description: str
    lessons: list[NormalLessonResponse]


# ── Kids mode ───────────────────────────────────────────────────────────


class KidsLessonResponse(BaseModel):
    title: str
    text_blocks: list[str]
    image_prompts: list[ImagePromptResponse] = []
    key_points: list[str]
    quiz: list[QuizQuestionResponse]


class KidsCoursePlanResponse(BaseModel):
    title: str
    description: str
    lessons: list[KidsLessonResponse]


# ── Advanced mode ───────────────────────────────────────────────────────


class ResearchPlanResponse(BaseModel):
    queries: list[str]


class AdvancedLessonResponse(BaseModel):
    title: str
    content: str
    cited_sources: list[int] = []
    key_points: list[str]
    quiz: list[QuizQuestionResponse]


class AdvancedCoursePlanResponse(BaseModel):
    title: str
    description: str
    lessons: list[AdvancedLessonResponse]


# ── Search ──────────────────────────────────────────────────────────────


class SearchResultResponse(BaseModel):
    title: str
    url: str
    snippet: str


class SearchResponse(BaseModel):
    results: list[SearchResultResponse]
