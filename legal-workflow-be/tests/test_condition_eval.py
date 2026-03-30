"""Step 19: Condition Evaluator tests."""

import pytest
import json
from src.modules.workflow.condition_evaluator import evaluate_condition


class TestConditionEvaluator:

    def test_none_condition_returns_true(self):
        """None condition -> True (auto-match)."""
        assert evaluate_condition(None, {}) is True

    def test_less_than_true(self):
        """Less than condition evaluates correctly when true."""
        expr = json.dumps({"<": [{"var": "round_count"}, 3]})
        assert evaluate_condition(expr, {"round_count": 1}) is True

    def test_less_than_false(self):
        """Less than condition evaluates correctly when false."""
        expr = json.dumps({"<": [{"var": "round_count"}, 3]})
        assert evaluate_condition(expr, {"round_count": 5}) is False

    def test_equals_true(self):
        """Equals condition evaluates correctly when true."""
        expr = json.dumps({"==": [{"var": "all_agreed"}, True]})
        assert evaluate_condition(expr, {"all_agreed": True}) is True

    def test_equals_false(self):
        """Equals condition evaluates correctly when false."""
        expr = json.dumps({"==": [{"var": "all_agreed"}, True]})
        assert evaluate_condition(expr, {"all_agreed": False}) is False

    def test_and_compound(self):
        """AND compound condition works."""
        expr = json.dumps({
            "and": [
                {"<": [{"var": "round_count"}, 3]},
                {"==": [{"var": "approved"}, True]},
            ]
        })
        assert evaluate_condition(expr, {"round_count": 1, "approved": True}) is True
        assert evaluate_condition(expr, {"round_count": 5, "approved": True}) is False

    def test_or_compound(self):
        """OR compound condition works."""
        expr = json.dumps({
            "or": [
                {"==": [{"var": "status"}, "fast_track"]},
                {"<": [{"var": "priority"}, 2]},
            ]
        })
        assert evaluate_condition(expr, {"status": "normal", "priority": 1}) is True
        assert evaluate_condition(expr, {"status": "fast_track", "priority": 5}) is True
        assert evaluate_condition(expr, {"status": "normal", "priority": 5}) is False
