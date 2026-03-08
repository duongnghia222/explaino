"""
AI Service for Explanation Generation
"""

from __future__ import annotations

import json
import logging

from openai import OpenAIError

from src.config import settings
from src.services.ai_client import AIServiceError, client

logger = logging.getLogger(__name__)


async def generate_explanation(
    text: str,
    thread: list[dict[str, str]] | None = None,
) -> dict:
    """Generate an explanation and key terms for the given text.

    Args:
        text: The current question / term to explain.
        thread: Prior conversation turns (oldest first). Each dict has
                "text" (user question) and "explanation" (assistant answer).

    Returns a dict with keys "explanation" (str) and "key_terms" (list[str]).
    """
    system_prompt = (
        "You are a knowledgeable AI assistant. Provide clear, helpful, and accurate "
        "responses to any question or topic. Also identify 3-5 related topics or key "
        "terms the reader might want to explore further. If no meaningful related "
        "topics exist, return an empty array. Return your response as JSON with two keys: "
        '"explanation" (string, markdown) and "key_terms" (array of strings).'
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    # Replay the full conversation thread so the model has context
    if thread:
        for turn in thread:
            messages.append({"role": "user", "content": turn["text"]})
            messages.append({"role": "assistant", "content": turn["explanation"]})

    # Current question
    messages.append({"role": "user", "content": text})

    try:
        response = await client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
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
