"""
Explanation Data Models
Pydantic models for explanation requests and responses
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ExplanationRequest(BaseModel):
    text: str
    parent_id: str | None = None
    is_follow_up: bool = False


class ExplanationRecord(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    is_follow_up: bool = False
    created_at: datetime


class ExplanationResponse(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    is_follow_up: bool = False
    created_at: datetime


class ExplanationNode(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    is_follow_up: bool = False
    children: list[ExplanationNode] = []
    depth: int = 0


ExplanationNode.model_rebuild()
