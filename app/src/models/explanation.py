"""
Explanation Data Models
Pydantic models for explanation requests and responses
"""

# TODO: Implement Pydantic models
# - ExplanationRequest: Input model for explanation generation
#   - text: str (text to explain)
#   - context: Optional[str] (additional context)
#   - parent_id: Optional[str] (parent explanation ID for nested explanations)
#
# - ExplanationResponse: Output model for generated explanations
#   - id: str (unique explanation ID)
#   - text: str (original text)
#   - explanation: str (AI-generated explanation)
#   - parent_id: Optional[str]
#   - created_at: datetime
#
# - ExplanationNode: Model for tree structure
#   - id: str
#   - text: str
#   - explanation: str
#   - parent_id: Optional[str]
#   - children: List[ExplanationNode]
#   - depth: int
