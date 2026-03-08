"""
Shared AI clients and base error class.
"""

from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI

from src.config import settings

# LangChain chat models for structured output
chat_model = ChatOpenAI(
    model=settings.openrouter_model,
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)

search_model = ChatOpenAI(
    model=settings.deep_research_model,
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)

# Raw OpenAI client kept for image generation only
image_client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.openrouter_base_url,
)


class AIServiceError(Exception):
    """Raised when the AI service encounters an error."""
