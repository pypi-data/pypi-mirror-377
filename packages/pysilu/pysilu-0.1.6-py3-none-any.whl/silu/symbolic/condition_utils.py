#!/usr/bin/env python3
"""
Condition Processing Utilities for Symbolic Execution

This module provides utilities for handling path conditions, simplifying expressions,
and managing condition-related operations in symbolic execution.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# Z3 availability check
try:
    import z3  # noqa: F401
    from z3 import Not

    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False


@dataclass
class PathCondition:
    """Represents a condition that must be satisfied for a path to be taken"""

    expression: str
    is_true: bool
    raw_expression: Optional[Any] = None
    source_line: Optional[int] = None
    z3_constraint: Optional[Any] = None

    def __str__(self) -> str:
        if self.is_true:
            return self.expression
        else:
            # Check if expression already starts with 'not'
            if self.expression.strip().startswith("not "):
                # Double negation: remove the 'not'
                inner_expr = self.expression.strip()[4:].strip()
                if inner_expr.startswith("(") and inner_expr.endswith(")"):
                    inner_expr = inner_expr[1:-1].strip()
                return inner_expr
            else:
                # Check if expression needs parentheses for negation
                if self._is_simple_expression(self.expression):
                    return f"not {self.expression}"
                else:
                    return f"not ({self.expression})"

    def _is_simple_expression(self, expr: str) -> bool:
        """Check if expression is simple enough to not need parentheses when negated"""
        expr = expr.strip()

        # If it contains boolean operators, it's compound and needs parentheses
        if " and " in expr or " or " in expr:
            return False

        # If it already starts with 'not', it might need parentheses
        if expr.startswith("not "):
            return False

        # Check for simple comparison patterns
        comparison_patterns = [
            r"\w+\s*>=\s*\w+",  # x >= y
            r"\w+\s*<=\s*\w+",  # x <= y
            r"\w+\s*==\s*\w+",  # x == y
            r"\w+\s*!=\s*\w+",  # x != y
            r"\w+\s*>\s*\w+",  # x > y
            r"\w+\s*<\s*\w+",  # x < y
        ]

        import re

        for pattern in comparison_patterns:
            if re.match(pattern, expr):
                return True

        # Single identifier is simple
        if expr.isidentifier():
            return True

        # Function calls are simple if they don't contain operators
        if (
            "(" in expr
            and ")" in expr
            and not any(op in expr for op in [" and ", " or ", " not "])
        ):
            return True

        return False

    def negate(self) -> "PathCondition":
        """Return the negated condition"""
        negated_constraint = None
        if self.z3_constraint is not None and Z3_AVAILABLE:
            negated_constraint = Not(self.z3_constraint)

        # Handle logical negation properly
        if self.is_true:
            # Currently true, make it false (add negation)
            return PathCondition(
                expression=self.expression,
                is_true=False,
                raw_expression=self.raw_expression,
                source_line=self.source_line,
                z3_constraint=negated_constraint,
            )
        else:
            # Currently false (already negated), make it true (remove negation)
            # Try to simplify double negation
            expr = self.expression.strip()
            if expr.startswith("not "):
                # Remove the 'not' prefix
                inner_expr = expr[4:].strip()
                if inner_expr.startswith("(") and inner_expr.endswith(")"):
                    inner_expr = inner_expr[1:-1].strip()
                return PathCondition(
                    expression=inner_expr,
                    is_true=True,
                    raw_expression=self.raw_expression, # Keep original raw expression
                    source_line=self.source_line,
                    z3_constraint=negated_constraint,
                )
            else:
                # Standard negation: flip is_true
                return PathCondition(
                    expression=self.expression,
                    is_true=True,
                    raw_expression=self.raw_expression, # Keep original raw expression
                    source_line=self.source_line,
                    z3_constraint=negated_constraint,
                )


def extract_variable_from_condition(condition_str: str) -> Optional[str]:
    """
    Extract variable name from a simple condition like 'x > 5'

    Args:
        condition_str: String representation of the condition

    Returns:
        Variable name if found, None otherwise
    """
    condition_str = condition_str.strip()

    # Pattern for simple variable comparisons: variable op value
    pattern = r"^(\w+)\s*([><=!]+)\s*(.+)$"
    match = re.match(pattern, condition_str)

    if match:
        var_name = match.group(1)
        # Check if this is a simple variable (not a function call or complex expression)
        if var_name.isidentifier():
            return var_name

    return None


def is_simple_variable_condition(condition_str: str) -> bool:
    """Check if condition is a simple variable comparison"""
    return extract_variable_from_condition(condition_str) is not None


def group_conditions_by_variable(
    conditions: List[PathCondition],
) -> Dict[str, List[PathCondition]]:
    """
    Group conditions by the variable they reference

    Args:
        conditions: List of path conditions

    Returns:
        Dictionary mapping variable names to their conditions
    """
    groups = {}

    for condition in conditions:
        var_name = extract_variable_from_condition(condition.expression)
        if var_name:
            if var_name not in groups:
                groups[var_name] = []
            groups[var_name].append(condition)

    return groups


def merge_conditions_for_variable(
    variable: str, conditions: List[PathCondition]
) -> List[PathCondition]:
    """
    Merge conditions for a single variable

    Args:
        variable: Variable name
        conditions: List of conditions for this variable

    Returns:
        List of merged/simplified conditions
    """
    if len(conditions) <= 1:
        return conditions

    # Separate positive and negative conditions
    positive_conditions = [c for c in conditions if c.is_true]
    negative_conditions = [c for c in conditions if not c.is_true]

    # Try to merge negative conditions (not operators)
    merged_negative = merge_negative_conditions(variable, negative_conditions)

    # For now, just return original conditions if no simplification
    # More sophisticated merging could be implemented here
    return positive_conditions + merged_negative


def merge_negative_conditions(
    variable: str, negative_conditions: List[PathCondition]
) -> List[PathCondition]:
    """
    Merge negative conditions for a variable

    Args:
        variable: Variable name
        negative_conditions: List of negative conditions (is_true=False)

    Returns:
        List of merged negative conditions converted to positive form
    """
    if len(negative_conditions) <= 1:
        # Still convert single negative conditions to positive form
        if len(negative_conditions) == 1 and not negative_conditions[0].is_true:
            return [
                _convert_negative_condition_to_positive(
                    negative_conditions[0], variable
                )
            ]
        return negative_conditions

    # Separate conditions by type and convert negative to positive
    gt_values = []  # from "not (x > value)" -> "x <= value"
    lt_values = []  # from "not (x < value)" -> "x >= value"
    converted_conditions = []
    other_conditions = []

    for condition in negative_conditions:
        # Skip conditions that are not actually negative
        if condition.is_true:
            other_conditions.append(condition)
            continue

        expr = condition.expression.strip()

        # Parse "x > value" patterns (when is_true=False, this means "not (x > value)" -> "x <= value")
        gt_match = re.match(rf"^{re.escape(variable)}\s*>\s*(.+)$", expr)
        if gt_match:
            try:
                value = float(gt_match.group(1))
                gt_values.append((value, condition))
                continue
            except ValueError:
                pass

        # Parse "x < value" patterns (when is_true=False, this means "not (x < value)" -> "x >= value")
        lt_match = re.match(rf"^{re.escape(variable)}\s*<\s*(.+)$", expr)
        if lt_match:
            try:
                value = float(lt_match.group(1))
                lt_values.append((value, condition))
                continue
            except ValueError:
                pass

        # For other patterns, convert directly
        converted = _convert_negative_condition_to_positive(condition, variable)
        converted_conditions.append(converted)

    # Merge gt conditions: "not (x > a)" and "not (x > b)" -> "x <= min(a,b)"
    if gt_values:
        min_value = min(value for value, _ in gt_values)
        original_condition = next(cond for val, cond in gt_values if val == min_value)
        formatted_value = int(min_value) if min_value.is_integer() else min_value
        converted_conditions.append(
            PathCondition(
                f"{variable} <= {formatted_value}", True, original_condition.raw_expression, original_condition.source_line
            )
        )

    # Merge lt conditions: "not (x < a)" and "not (x < b)" -> "x >= max(a,b)"
    if lt_values:
        max_value = max(value for value, _ in lt_values)
        original_condition = next(cond for val, cond in lt_values if val == max_value)
        formatted_value = int(max_value) if max_value.is_integer() else max_value
        converted_conditions.append(
            PathCondition(
                f"{variable} >= {formatted_value}", True, original_condition.raw_expression, original_condition.source_line
            )
        )

    # Add any non-negative conditions unchanged
    converted_conditions.extend(other_conditions)

    return converted_conditions


def _convert_negative_condition_to_positive(
    condition: PathCondition, variable: str
) -> PathCondition:
    """
    Convert a single negative condition to its positive equivalent

    Args:
        condition: Negative condition (is_true=False)
        variable: Variable name

    Returns:
        Converted positive condition
    """
    if condition.is_true:
        return condition

    expr = condition.expression.strip()

    # Parse different comparison patterns - order matters: compound operators first
    patterns = [
        (rf"^{re.escape(variable)}\s*>=\s*(.+)$", "<"),  # x >= v -> x < v
        (rf"^{re.escape(variable)}\s*<=\s*(.+)$", ">"),  # x <= v -> x > v
        (rf"^{re.escape(variable)}\s*==\s*(.+)$", "!="),  # x == v -> x != v
        (rf"^{re.escape(variable)}\s*!=\s*(.+)$", "=="),  # x != v -> x == v
        (rf"^{re.escape(variable)}\s*>\s*(.+)$", "<="),  # x > v -> x <= v
        (rf"^{re.escape(variable)}\s*<\s*(.+)$", ">="),  # x < v -> x >= v
    ]

    for pattern, new_op in patterns:
        match = re.match(pattern, expr)
        if match:
            value_str = match.group(1).strip()
            new_expr = f"{variable} {new_op} {value_str}"

            return PathCondition(
                new_expr, True, condition.raw_expression, condition.source_line, condition.z3_constraint
            )

    # If no pattern matches, return the condition unchanged but marked as problematic
    return PathCondition(
        f"not ({expr})", True, condition.raw_expression, condition.source_line, condition.z3_constraint
    )


def simplify_condition_expression(expression: str) -> str:
    """
    Simplify a condition expression by removing redundant parts

    Args:
        expression: String representation of condition

    Returns:
        Simplified expression string
    """
    if expression is None:
        return ""
    if not isinstance(expression, str):
        return str(expression)
    if not expression.strip():
        return ""

    # Remove extra whitespace
    expr = re.sub(r"\s+", " ", expression.strip())

    if not expr:
        return expr

    # Remove redundant parentheses around simple expressions
    if expr.startswith("(") and expr.endswith(")") and len(expr) > 2:
        # Check if parentheses are actually redundant
        paren_count = 0
        can_remove = True
        inner_expr = expr[1:-1]  # Content inside outer parentheses

        for char in inner_expr:
            if char == "(":
                paren_count += 1
            elif char == ")":
                paren_count -= 1
                if paren_count < 0:  # More closing than opening parens
                    can_remove = False
                    break

        if can_remove and paren_count == 0:
            expr = inner_expr.strip()

    # Normalize comparison operators with proper spacing
    # Order matters: do compound operators first to avoid conflicts
    expr = re.sub(r"\s*<=\s*", " <= ", expr)
    expr = re.sub(r"\s*>=\s*", " >= ", expr)
    expr = re.sub(r"\s*==\s*", " == ", expr)
    expr = re.sub(r"\s*!=\s*", " != ", expr)

    # Handle single character operators (avoid conflicts with compound ones)
    expr = re.sub(r"(?<!<|>|=|!)\s*>\s*(?!=)", " > ", expr)
    expr = re.sub(r"(?<!<|>|=|!)\s*<\s*(?!=)", " < ", expr)

    # Normalize boolean operators
    expr = re.sub(r"\s+and\s+", " and ", expr)
    expr = re.sub(r"\s+or\s+", " or ", expr)
    expr = re.sub(r"\s+not\s+", " not ", expr)

    return expr.strip()


def make_condition_readable(condition_str: str) -> str:
    """
    Make a condition more readable by improving formatting and simplifying

    Args:
        condition_str: String representation of condition

    Returns:
        More readable condition string
    """
    if not condition_str or not isinstance(condition_str, str):
        return str(condition_str) if condition_str is not None else ""

    condition_str = condition_str.strip()

    # Handle tuple expressions from symbolic execution
    if (
        condition_str.startswith("(")
        and "," in condition_str
        and condition_str.endswith(")")
    ):
        try:
            # Try to parse as tuple and make it readable
            import ast

            parsed = ast.literal_eval(condition_str)
            if isinstance(parsed, tuple) and len(parsed) >= 2:
                op = parsed[0]
                if op in [">", "<", ">=", "<=", "==", "!="]:
                    left = str(parsed[1]) if len(parsed) > 1 else "?"
                    right = str(parsed[2]) if len(parsed) > 2 else "?"
                    return f"{left} {op} {right}"
                elif op == "And":
                    conditions = [
                        make_condition_readable(str(cond)) for cond in parsed[1:]
                    ]
                    return " and ".join(conditions) if conditions else ""
                elif op == "Or":
                    conditions = [
                        make_condition_readable(str(cond)) for cond in parsed[1:]
                    ]
                    return " or ".join(conditions) if conditions else ""
        except (ValueError, SyntaxError, TypeError):
            # If parsing fails, continue with string processing
            pass

    # Handle Z3-style expressions
    if any(z3_op in condition_str for z3_op in ["And(", "Or(", "Not("]):
        try:
            # Convert Z3-style to readable format
            readable_str = condition_str

            # Handle And() expressions
            readable_str = re.sub(r"And\(([^)]+)\)", r"(\1)", readable_str)

            # Handle Or() expressions
            readable_str = re.sub(r"Or\(([^)]+)\)", r"(\1)", readable_str)

            # Handle Not() expressions
            readable_str = re.sub(r"Not\(([^)]+)\)", r"not (\1)", readable_str)

            # Replace comma separators with appropriate operators
            # This is a simplified approach - in practice, we'd need more sophisticated parsing
            readable_str = re.sub(r",\s*", " and ", readable_str)

            condition_str = readable_str
        except Exception:
            # If Z3 processing fails, continue with original string
            pass

    return simplify_condition_expression(condition_str)


def split_condition_args(args_str: str) -> List[str]:
    """
    Split condition arguments, handling nested parentheses

    Args:
        args_str: String containing comma-separated arguments

    Returns:
        List of argument strings
    """
    args = []
    current_arg = ""
    paren_count = 0

    for char in args_str:
        if char == "," and paren_count == 0:
            args.append(current_arg.strip())
            current_arg = ""
        else:
            if char == "(":
                paren_count += 1
            elif char == ")":
                paren_count -= 1
            current_arg += char

    # Add the last argument
    if current_arg.strip():
        args.append(current_arg.strip())

    return args


def normalize_condition(condition: PathCondition) -> PathCondition:
    """
    Normalize a condition to a standard form

    Args:
        condition: Path condition to normalize

    Returns:
        Normalized path condition
    """
    expr = condition.expression.strip()
    is_true = condition.is_true

    # Handle double negation: if we have "not expr" and is_true=False,
    # this means "not (not expr)" which simplifies to "expr" with is_true=True
    if expr.startswith("not ") and not is_true:
        # Extract the inner expression
        inner_expr = expr[4:].strip()
        # Remove outer parentheses if they exist
        if inner_expr.startswith("(") and inner_expr.endswith(")"):
            inner_expr = inner_expr[1:-1].strip()
        return PathCondition(
            inner_expr, True, condition.raw_expression, condition.source_line, condition.z3_constraint
        )

    # Handle case where expression doesn't start with "not" but is_true=False
    # This represents a negated condition that should be normalized
    if not is_true and not expr.startswith("not "):
        # For simple expressions, we can try to convert to positive form
        # e.g., "x > 5" with is_true=False becomes "x <= 5" with is_true=True
        var_name = extract_variable_from_condition(expr)
        if var_name:
            converted = _convert_negative_condition_to_positive(condition, var_name)
            if converted.expression != expr or converted.is_true:
                return converted

    # Simplify the expression
    simplified_expr = make_condition_readable(expr)

    return PathCondition(
        simplified_expr, is_true, condition.raw_expression, condition.source_line, condition.z3_constraint
    )


def conditions_are_contradictory(cond1: PathCondition, cond2: PathCondition) -> bool:
    """
    Check if two conditions are contradictory

    Args:
        cond1: First condition
        cond2: Second condition

    Returns:
        True if conditions contradict each other
    """
    # Normalize both conditions
    norm1 = normalize_condition(cond1)
    norm2 = normalize_condition(cond2)

    # Check if they're exact opposites
    if norm1.expression == norm2.expression:
        return norm1.is_true != norm2.is_true

    # Check for some simple contradictions
    # e.g., "x > 5" and "x < 3"
    var1 = extract_variable_from_condition(norm1.expression)
    var2 = extract_variable_from_condition(norm2.expression)

    if var1 and var2 and var1 == var2:
        # Same variable, check for contradictory ranges
        return check_range_contradiction(norm1, norm2, var1)

    return False


def check_range_contradiction(
    cond1: PathCondition, cond2: PathCondition, variable: str
) -> bool:
    """
    Check if two conditions on the same variable create a contradiction

    Args:
        cond1: First condition
        cond2: Second condition
        variable: Variable name

    Returns:
        True if conditions are contradictory
    """

    def parse_range_condition(cond: PathCondition) -> Optional[Tuple[str, float, bool]]:
        """Parse condition like 'x > 5' into (op, value, is_true)"""
        expr = cond.expression.strip()
        # Check operators in order of length to avoid partial matches
        for op in [">=", "<=", "==", "!=", ">", "<"]:
            if f" {op} " in expr:  # Ensure proper spacing to avoid partial matches
                parts = expr.split(f" {op} ")
                if len(parts) == 2:
                    var_part = parts[0].strip()
                    val_part = parts[1].strip()
                    if var_part == variable:
                        try:
                            value = float(val_part)
                            return (op, value, cond.is_true)
                        except ValueError:
                            pass
        return None

    parsed1 = parse_range_condition(cond1)
    parsed2 = parse_range_condition(cond2)

    if not parsed1 or not parsed2:
        return False

    op1, val1, true1 = parsed1
    op2, val2, true2 = parsed2

    # Check contradictions when both conditions must be true
    if true1 and true2:
        # x > a and x < b where a >= b
        if op1 == ">" and op2 == "<" and val1 >= val2:
            return True
        if op2 == ">" and op1 == "<" and val2 >= val1:
            return True

        # x >= a and x < b where a >= b
        if op1 == ">=" and op2 == "<" and val1 >= val2:
            return True
        if op2 == ">=" and op1 == "<" and val2 >= val1:
            return True

        # x > a and x <= b where a >= b
        if op1 == ">" and op2 == "<=" and val1 >= val2:
            return True
        if op2 == ">" and op1 == "<=" and val2 >= val1:
            return True

        # x >= a and x <= b where a > b
        if op1 == ">=" and op2 == "<=" and val1 > val2:
            return True
        if op2 == ">=" and op1 == "<=" and val2 > val1:
            return True

        # x == a and x != a
        if op1 == "==" and op2 == "!=" and val1 == val2:
            return True
        if op2 == "==" and op1 == "!=" and val2 == val1:
            return True

        # x == a and x > a (or x < a, x >= a+1, x <= a-1, etc.)
        if op1 == "==" and op2 == ">" and val1 <= val2:
            return True
        if op2 == "==" and op1 == ">" and val2 <= val1:
            return True
        if op1 == "==" and op2 == "<" and val1 >= val2:
            return True
        if op2 == "==" and op1 == "<" and val2 >= val1:
            return True

    # Check contradictions when one is true and one is false
    elif true1 != true2:
        # If the conditions are identical but one is negated
        if op1 == op2 and val1 == val2:
            return True

    return False


def simplify_conditions_list(conditions: List[PathCondition]) -> List[PathCondition]:
    """
    Simplify a list of conditions by removing redundancies and contradictions

    Args:
        conditions: List of path conditions

    Returns:
        Simplified list of conditions
    """
    if not conditions:
        return conditions

    # Normalize all conditions first to handle double negations
    normalized_conditions = [normalize_condition(cond) for cond in conditions]

    # Remove exact duplicates after normalization
    seen = set()
    unique_conditions = []
    for cond in normalized_conditions:
        cond_key = (cond.expression, cond.is_true)
        if cond_key not in seen:
            seen.add(cond_key)
            unique_conditions.append(cond)

    # Separate simple variable conditions from complex ones
    simple_conditions = []
    complex_conditions = []

    for condition in unique_conditions:
        if is_simple_variable_condition(condition.expression):
            simple_conditions.append(condition)
        else:
            complex_conditions.append(condition)

    # Group simple conditions by variable for potential simplification
    grouped_conditions = group_conditions_by_variable(simple_conditions)

    # Simplify conditions for each variable group
    simplified_simple_conditions = []
    for var_name, conditions_for_var in grouped_conditions.items():
        if var_name and len(conditions_for_var) > 1:
            # Use the enhanced variable-level merging strategy
            merged_conditions = merge_conditions_for_variable(
                var_name, conditions_for_var
            )
            simplified_simple_conditions.extend(merged_conditions)
        else:
            simplified_simple_conditions.extend(conditions_for_var)

    # Combine simplified simple conditions with complex conditions
    all_simplified = simplified_simple_conditions + complex_conditions

    # Check for contradictions and remove them
    final_simplified = []
    contradictory_pairs = set()

    for i, cond in enumerate(all_simplified):
        is_contradictory = False

        # Check against already accepted conditions
        for j, existing in enumerate(final_simplified):
            if conditions_are_contradictory(cond, existing):
                # Mark as contradictory but don't add either
                contradictory_pairs.add((i, j))
                is_contradictory = True
                break

        if not is_contradictory:
            final_simplified.append(cond)

    return final_simplified
