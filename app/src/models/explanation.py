"""
Explanation Data Models
Pydantic models for explanation requests and responses
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator

InputType = Literal["text", "file", "url"]


class ExplanationRequest(BaseModel):
    text: str = ""
    url: str | None = None
    input_type: InputType = "text"
    parent_id: str | None = None
    is_follow_up: bool = False

    @model_validator(mode="after")
    def validate_input(self) -> ExplanationRequest:
        if self.input_type in ("text", "file"):
            if not self.text or not self.text.strip():
                raise ValueError("text must be non-empty for text/file input")
        elif self.input_type == "url":
            if not self.url or not self.url.strip():
                raise ValueError("url must be non-empty for url input")
        return self


class ExplanationRecord(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    is_follow_up: bool = False
    input_type: str = "text"
    source_url: str | None = None
    created_at: datetime


class ExplanationResponse(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    is_follow_up: bool = False
    input_type: str = "text"
    source_url: str | None = None
    created_at: datetime


class ExplanationNode(BaseModel):
    id: str
    text: str
    explanation: str
    key_terms: list[str]
    parent_id: str | None = None
    is_follow_up: bool = False
    input_type: str = "text"
    source_url: str | None = None
    children: list[ExplanationNode] = []
    depth: int = 0


ExplanationRequest.model_rebuild()
ExplanationNode.model_rebuild()
