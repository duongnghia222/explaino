"""
AI Service for Explanation and Course Generation
Handles interaction with OpenAI API
"""

from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI, OpenAIError

from src.config import settings

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)


class AIServiceError(Exception):
    """Raised when the AI service encounters an error."""


async def generate_explanation(
    text: str,
    context: str | None = None,
    parent_text: str | None = None,
    parent_explanation: str | None = None,
) -> dict:
    """Generate an explanation and key terms for the given text.

    Returns a dict with keys "explanation" (str) and "key_terms" (list[str]).
    """
    system_prompt = (
        "You are a knowledgeable AI assistant. Provide clear, helpful, and accurate "
        "responses to any question or topic. Also identify 3-5 related topics or key "
        "terms the reader might want to explore further. If no meaningful related "
        "topics exist, return an empty array. Return your response as JSON with two keys: "
        '"explanation" (string, markdown) and "key_terms" (array of strings).'
    )

    user_parts: list[str] = [text]
    if context:
        user_parts.append(f"Additional context: {context}")
    if parent_text and parent_explanation:
        user_parts.append(
            f'The user previously asked: "{parent_text}"\n\n'
            f"The response was:\n{parent_explanation}\n\n"
            f"Now they want to explore further."
        )

    user_prompt = "\n\n".join(user_parts)

    try:
        response = await _client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if content is None:
            raise AIServiceError("Empty response from OpenRouter")

        data = json.loads(content)

        explanation = data.get("explanation", "")
        key_terms = data.get("key_terms", [])

        if not explanation:
            raise AIServiceError("No explanation in AI response")
        if not isinstance(key_terms, list):
            key_terms = []

        return {"explanation": explanation, "key_terms": key_terms[:5]}

    except OpenAIError as exc:
        logger.error("OpenRouter API error: %s", exc)
        raise AIServiceError(f"OpenRouter API error: {exc}") from exc
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI response: %s", exc)
        raise AIServiceError("Invalid JSON in AI response") from exc


async def generate_course(topic: str, mode: str) -> dict:
    """Generate a structured course on the given topic.

    Returns a dict with keys: title, description, lessons.
    Each lesson has: title, content, key_points, quiz.
    """
    mode_instructions = {
        "kids": (
            "Use simple language suitable for children ages 8-12. "
            "Make it fun, engaging, and use analogies kids can relate to. "
            "Keep sentences short and avoid jargon."
        ),
        "normal": (
            "Use clear, standard language suitable for a general adult audience. "
            "Balance depth with accessibility."
        ),
        "advanced": (
            "Use technical, in-depth language suitable for an expert audience. "
            "Include detailed nuances, advanced concepts, and precise terminology."
        ),
    }

    style = mode_instructions.get(mode, mode_instructions["normal"])

    system_prompt = (
        "You are an expert course creator. Generate a structured course on the "
        "given topic. Return your response as JSON with these keys:\n"
        '- "title": course title (string)\n'
        '- "description": brief course description (string)\n'
        '- "lessons": array of 4-6 lesson objects, each with:\n'
        '  - "title": lesson title (string)\n'
        '  - "content": detailed lesson content in markdown (string)\n'
        '  - "key_points": array of 3-5 key takeaways (strings)\n'
        '  - "quiz": array of 2-3 quiz question objects, each with:\n'
        '    - "question": the question (string)\n'
        '    - "options": array of 4 answer options (strings)\n'
        '    - "correct_index": index of the correct option (0-3)\n'
        '    - "explanation": why the correct answer is right (string)\n\n'
        f"Style instructions: {style}"
    )

    user_prompt = f"Create a course about: {topic}"

    try:
        response = await _client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if content is None:
            raise AIServiceError("Empty response from OpenRouter")

        data = json.loads(content)

        if "title" not in data or "lessons" not in data:
            raise AIServiceError("Missing required fields in AI course response")

        return {
            "title": data["title"],
            "description": data.get("description", ""),
            "lessons": data["lessons"],
        }

    except OpenAIError as exc:
        logger.error("OpenRouter API error: %s", exc)
        raise AIServiceError(f"OpenRouter API error: {exc}") from exc
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI response: %s", exc)
        raise AIServiceError("Invalid JSON in AI response") from exc
