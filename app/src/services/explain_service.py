"""
AI Service for Explanation Generation
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from src.services.ai_client import AIServiceError, chat_model

logger = logging.getLogger(__name__)


class ExplanationResponse(BaseModel):
    explanation: str
    key_terms: list[str] = []


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
        "responses to any question or topic. Respond in JSON format. Also identify 3-5 "
        "related topics or key terms the reader might want to explore further. If no "
        "meaningful related topics exist, return an empty array."
    )

    messages: list = [SystemMessage(content=system_prompt)]

    # Replay the full conversation thread so the model has context
    if thread:
        for turn in thread:
            messages.append(HumanMessage(content=turn["text"]))
            messages.append(AIMessage(content=turn["explanation"]))

    # Current question
    messages.append(HumanMessage(content=text))

    try:
        structured = chat_model.with_structured_output(
            ExplanationResponse, method="json_mode"
        )
        result = await structured.ainvoke(messages)

        if not result.explanation:
            raise AIServiceError("No explanation in AI response")

        return {
            "explanation": result.explanation,
            "key_terms": result.key_terms[:5],
        }

    except AIServiceError:
        raise
    except Exception as exc:
        logger.error("Explanation generation failed: %s", exc)
        raise AIServiceError(f"Explanation generation failed: {exc}") from exc
