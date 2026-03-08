"""
Explanation API Routes
Endpoints for explanation generation and retrieval
"""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from src.models.explanation import (
    ExplanationNode,
    ExplanationRecord,
    ExplanationRequest,
    ExplanationResponse,
)
from src.services.ai_service import generate_explanation
from src.services.storage import (
    build_tree,
    get_children,
    get_explanation,
    get_root_id,
    save_explanation,
)

router = APIRouter(prefix="/api/explain", tags=["explanations"])


@router.post("", response_model=ExplanationResponse)
async def create_explanation(request: ExplanationRequest) -> ExplanationResponse:
    """Generate a new explanation for the given text."""
    parent_text: str | None = None
    parent_explanation: str | None = None
    if request.parent_id:
        parent = get_explanation(request.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent explanation not found")
        parent_text = parent.text
        parent_explanation = parent.explanation

    result = await generate_explanation(
        text=request.text,
        context=request.context,
        parent_text=parent_text,
        parent_explanation=parent_explanation,
    )

    record = ExplanationRecord(
        id=str(uuid4()),
        text=request.text,
        explanation=result["explanation"],
        key_terms=result["key_terms"],
        parent_id=request.parent_id,
        created_at=datetime.now(timezone.utc),
    )
    save_explanation(record)

    return ExplanationResponse(**record.model_dump())


@router.get("/{id}", response_model=ExplanationResponse)
async def get_explanation_by_id(id: str) -> ExplanationResponse:
    """Retrieve a specific explanation by ID."""
    record = get_explanation(id)
    if record is None:
        raise HTTPException(status_code=404, detail="Explanation not found")
    return ExplanationResponse(**record.model_dump())


@router.get("/{id}/tree", response_model=ExplanationNode)
async def get_explanation_tree(id: str) -> ExplanationNode:
    """Get the full explanation tree starting from the root of the given node."""
    record = get_explanation(id)
    if record is None:
        raise HTTPException(status_code=404, detail="Explanation not found")

    root_id = get_root_id(id)
    tree = build_tree(root_id)
    if tree is None:
        raise HTTPException(status_code=404, detail="Root explanation not found")

    return tree


@router.get("/{id}/children", response_model=list[ExplanationResponse])
async def get_explanation_children(id: str) -> list[ExplanationResponse]:
    """Get direct children of an explanation."""
    record = get_explanation(id)
    if record is None:
        raise HTTPException(status_code=404, detail="Explanation not found")

    children = get_children(id)
    return [ExplanationResponse(**child.model_dump()) for child in children]
