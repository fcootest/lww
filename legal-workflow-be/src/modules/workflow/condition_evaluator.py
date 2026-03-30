"""Condition evaluator -- Simple JSON Logic evaluator for TNT conditions."""

import json


def evaluate_condition(expression, context):
    """Evaluate a condition expression against a context.

    Supports:
    - None -> True (auto-match)
    - {"<": [{"var": "x"}, N]} -> context[x] < N
    - {"==": [{"var": "x"}, val]} -> context[x] == val
    - {"and": [...]} -> all conditions true
    - {"or": [...]} -> any condition true
    """
    if expression is None:
        return True

    if isinstance(expression, str):
        expression = json.loads(expression)

    return _eval_node(expression, context)


def _eval_node(node, context):
    """Recursively evaluate a JSON Logic node."""
    if isinstance(node, bool):
        return node

    if isinstance(node, (int, float, str)):
        return node

    if isinstance(node, dict):
        if "var" in node:
            return context.get(node["var"])

        for op, args in node.items():
            if op == "<":
                left = _eval_node(args[0], context)
                right = _eval_node(args[1], context)
                if left is None or right is None:
                    return False
                return left < right

            elif op == "==":
                left = _eval_node(args[0], context)
                right = _eval_node(args[1], context)
                return left == right

            elif op == "and":
                return all(_eval_node(a, context) for a in args)

            elif op == "or":
                return any(_eval_node(a, context) for a in args)

            elif op == ">":
                left = _eval_node(args[0], context)
                right = _eval_node(args[1], context)
                if left is None or right is None:
                    return False
                return left > right

    return False
