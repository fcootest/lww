"""TSI Status Machine — valid status transitions."""

VALID_TRANSITIONS = {
    "DRAFT": ["IN_PROGRESS", "CANCELLED"],
    "IN_PROGRESS": ["COMPLETED", "SUBMITTED", "APPROVED", "REJECTED", "CANCELLED", "PENDING_REVIEW"],
    "PENDING": ["IN_PROGRESS", "SUBMITTED", "APPROVED", "REJECTED", "CANCELLED"],
    "SUBMITTED": ["APPROVED", "REJECTED", "IN_PROGRESS"],
    "PENDING_REVIEW": ["APPROVED", "REJECTED"],
    "APPROVED": ["COMPLETED"],
    "REJECTED": ["IN_PROGRESS", "SUBMITTED", "CANCELLED"],
    "COMPLETED": [],  # terminal
    "CANCELLED": [],  # terminal
}


def is_valid_transition(from_s: str, to_s: str) -> bool:
    """Check if a status transition is valid."""
    allowed = VALID_TRANSITIONS.get(from_s, [])
    return to_s in allowed


def assert_transition(from_s: str, to_s: str):
    """Assert a status transition is valid, raise ValueError if not."""
    if not is_valid_transition(from_s, to_s):
        raise ValueError(
            f"Invalid status transition from '{from_s}' to '{to_s}'. "
            f"Allowed transitions from '{from_s}': {VALID_TRANSITIONS.get(from_s, [])}"
        )
