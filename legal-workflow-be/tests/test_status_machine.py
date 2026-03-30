"""Step 16: TSI Status Machine tests."""

import pytest
from src.common.status_machine import is_valid_transition, assert_transition


class TestStatusMachine:

    def test_pending_to_in_progress_valid(self):
        """PENDING -> IN_PROGRESS is valid."""
        assert is_valid_transition("PENDING", "IN_PROGRESS") is True

    def test_in_progress_to_completed_valid(self):
        """IN_PROGRESS -> COMPLETED is valid."""
        assert is_valid_transition("IN_PROGRESS", "COMPLETED") is True

    def test_completed_to_in_progress_invalid(self):
        """COMPLETED -> IN_PROGRESS is invalid (terminal state)."""
        assert is_valid_transition("COMPLETED", "IN_PROGRESS") is False

    def test_draft_to_completed_invalid(self):
        """DRAFT -> COMPLETED is invalid (must go through IN_PROGRESS)."""
        assert is_valid_transition("DRAFT", "COMPLETED") is False

    def test_in_progress_to_rejected_valid(self):
        """IN_PROGRESS -> REJECTED is valid."""
        assert is_valid_transition("IN_PROGRESS", "REJECTED") is True

    def test_cancelled_to_anything_invalid(self):
        """CANCELLED -> anything is invalid (terminal state)."""
        assert is_valid_transition("CANCELLED", "IN_PROGRESS") is False
        assert is_valid_transition("CANCELLED", "DRAFT") is False
        assert is_valid_transition("CANCELLED", "COMPLETED") is False

    def test_assert_transition_raises_on_invalid(self):
        """assert_transition raises ValueError on invalid transition."""
        with pytest.raises(ValueError, match="Invalid status transition"):
            assert_transition("COMPLETED", "IN_PROGRESS")

    def test_assert_transition_passes_on_valid(self):
        """assert_transition does not raise on valid transition."""
        assert_transition("PENDING", "IN_PROGRESS")  # should not raise

    def test_rejected_to_in_progress_valid(self):
        """REJECTED -> IN_PROGRESS is valid (can retry)."""
        assert is_valid_transition("REJECTED", "IN_PROGRESS") is True

    def test_pending_review_to_approved_valid(self):
        """PENDING_REVIEW -> APPROVED is valid."""
        assert is_valid_transition("PENDING_REVIEW", "APPROVED") is True
