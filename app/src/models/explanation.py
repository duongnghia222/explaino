"""
Explanation Data Models
Pydantic models for explanation requests and responses
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ExplanationRequest(BaseModel):
    text: str
    context: str | None = None
    parent_id: str | None = None


class ExplanationRecord(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    created_at: datetime


class ExplanationResponse(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    created_at: datetime


class ExplanationNode(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    children: list[ExplanationNode] = []
    depth: int = 0


ExplanationNode.model_rebuild()
