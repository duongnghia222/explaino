"""
Explanation API Routes
Endpoints for explanation generation and retrieval
"""

# TODO: Implement FastAPI router for explanation endpoints
#
# Endpoints to implement:
#
# POST /api/explain
# - Generate a new explanation for given text
# - Request: ExplanationRequest
# - Response: ExplanationResponse
# - Calls AIService to generate explanation
#
# GET /api/explain/{explanation_id}
# - Retrieve a specific explanation by ID
# - Response: ExplanationResponse
#
# GET /api/explain/{explanation_id}/tree
# - Get the full explanation tree starting from a node
# - Response: ExplanationNode with all children
#
# GET /api/explain/{explanation_id}/children
# - Get direct children of an explanation
# - Response: List[ExplanationResponse]
