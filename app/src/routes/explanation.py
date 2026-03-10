"""
Explanation API Routes
Endpoints for explanation generation and retrieval
"""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from src.config import settings
from src.models.explanation import (
    ExplanationNode,
    ExplanationRecord,
    ExplanationRequest,
    ExplanationResponse,
)
from src.services.crawl_service import CrawlError, crawl_url
from src.services.explain_service import generate_explanation
from src.services.explain_storage import (
    build_tree,
    get_ancestor_chain,
    get_children,
    get_explanation,
    get_root_id,
    save_explanation,
)

router = APIRouter(prefix="/api/explain", tags=["explanations"])


@router.post("", response_model=ExplanationResponse)
async def create_explanation(request: ExplanationRequest) -> ExplanationResponse:
    """Generate a new explanation for the given text."""

    if request.input_type == "url":
        try:
            content = await crawl_url(request.url)
        except CrawlError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if len(content) > settings.max_input_chars:
            raise HTTPException(
                status_code=413,
                detail=f"Content exceeds {settings.max_input_chars} character limit",
            )

        record = ExplanationRecord(
            id=str(uuid4()),
            text=request.url,
            explanation=content,
            key_terms=[],
            parent_id=request.parent_id,
            is_follow_up=request.is_follow_up,
            input_type="url",
            source_url=request.url,
            created_at=datetime.now(timezone.utc),
        )
        save_explanation(record)
        return ExplanationResponse(**record.model_dump())

    if request.input_type == "file":
        if len(request.text) > settings.max_input_chars:
            raise HTTPException(
                status_code=413,
                detail=f"Content exceeds {settings.max_input_chars} character limit",
            )

        first_line = request.text.split("\n", 1)[0].strip()[:100] or "Uploaded file"

        record = ExplanationRecord(
            id=str(uuid4()),
            text=first_line,
            explanation=request.text,
            key_terms=[],
            parent_id=request.parent_id,
            is_follow_up=request.is_follow_up,
            input_type="file",
            created_at=datetime.now(timezone.utc),
        )
        save_explanation(record)
        return ExplanationResponse(**record.model_dump())

    # Default: text input — existing AI flow
    if len(request.text) > settings.max_input_chars:
        raise HTTPException(
            status_code=413,
            detail=f"Content exceeds {settings.max_input_chars} character limit",
        )

    thread: list[dict[str, str]] | None = None
    if request.parent_id:
        parent = get_explanation(request.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent explanation not found")
        # Build full conversation thread from root to parent
        ancestors = get_ancestor_chain(request.parent_id)
        thread = [
            {"text": a.text, "explanation": a.explanation}
            for a in ancestors
        ]

    result = await generate_explanation(
        text=request.text,
        thread=thread,
    )

    record = ExplanationRecord(
        id=str(uuid4()),
        text=request.text,
        explanation=result["explanation"],
        key_terms=result["key_terms"],
        parent_id=request.parent_id,
        is_follow_up=request.is_follow_up,
        input_type="text",
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
