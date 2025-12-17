"""
AI Service for Explanation Generation
Handles interaction with OpenAI API
"""

# TODO: Implement AIService class
#
# Class: AIService
# - __init__(api_key: str, model: str)
# - async generate_explanation(text: str, context: Optional[str] = None) -> str
#   - Constructs prompt for OpenAI
#   - Calls OpenAI API to generate explanation
#   - Returns the generated explanation text
#
# Prompt Engineering:
# - System prompt: "You are an expert explainer. Generate clear, concise explanations..."
# - User prompt: Include the text to explain and any context
# - For nested explanations: Include parent explanation as context
#
# Error Handling:
# - Handle OpenAI API errors
# - Handle rate limiting
# - Validate responses
#
# Example usage:
# ai_service = AIService(api_key="...", model="gpt-4-turbo-preview")
# explanation = await ai_service.generate_explanation(
#     text="quantum entanglement",
#     context="Explaining to a high school student"
# )
