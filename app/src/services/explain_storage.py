"""
In-Memory Storage for Explanations
"""

from src.models.explanation import ExplanationNode, ExplanationRecord

_explanations: dict[str, ExplanationRecord] = {}
_children_index: dict[str, list[str]] = {}  # parent_id -> [child_ids]


def save_explanation(record: ExplanationRecord) -> None:
    """Save an explanation record and update the children index."""
    _explanations[record.id] = record
    if record.parent_id is not None:
        _children_index.setdefault(record.parent_id, []).append(record.id)


def get_explanation(id: str) -> ExplanationRecord | None:
    """Retrieve an explanation by ID."""
    return _explanations.get(id)


def get_children(parent_id: str) -> list[ExplanationRecord]:
    """Get direct children of an explanation."""
    child_ids = _children_index.get(parent_id, [])
    return [_explanations[cid] for cid in child_ids if cid in _explanations]


def get_ancestor_chain(id: str) -> list[ExplanationRecord]:
    """Walk up the parent chain and return ancestors from root to the given node."""
    chain: list[ExplanationRecord] = []
    current_id: str | None = id
    while current_id:
        record = _explanations.get(current_id)
        if record is None:
            break
        chain.append(record)
        current_id = record.parent_id
    chain.reverse()
    return chain


def get_root_id(id: str) -> str:
    """Walk up the parent chain to find the root explanation ID."""
    current_id = id
    while True:
        record = _explanations.get(current_id)
        if record is None or record.parent_id is None:
            return current_id
        current_id = record.parent_id


def build_tree(node_id: str, depth: int = 0) -> ExplanationNode | None:
    """Recursively build an explanation tree from a given node."""
    record = _explanations.get(node_id)
    if record is None:
        return None

    children_records = get_children(node_id)
    children_nodes = []
    for child in children_records:
        child_node = build_tree(child.id, depth=depth + 1)
        if child_node is not None:
            children_nodes.append(child_node)

    return ExplanationNode(
        id=record.id,
        text=record.text,
        explanation=record.explanation,
        key_terms=record.key_terms,
        parent_id=record.parent_id,
        is_follow_up=record.is_follow_up,
        children=children_nodes,
        depth=depth,
    )
