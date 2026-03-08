"""
Shared AI client and base error class.
"""

from openai import AsyncOpenAI

from src.config import settings

client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)


class AIServiceError(Exception):
    """Raised when the AI service encounters an error."""
