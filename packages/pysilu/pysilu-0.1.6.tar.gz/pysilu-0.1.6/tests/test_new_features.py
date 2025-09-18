"""
Unit tests for new Silu language features.

Tests for break/continue statements, assert statements,
annotated assignments, and lambda functions.
"""

import ast
import pytest
from silu.interpreter import SiluInterpreter


class TestBreakContinue:
    """Test break and continue statements."""

    @pytest.mark.parametrize(
        "loop_type,control,expected_result",
        [
            ("while", "break", [1, 2]),  # while with break
            ("while", "continue", [1, 2, 4, 5]),  # while with continue
            ("for", "break", [1, 2, 3]),  # for with break
            ("for", "continue", [1, 2, 4, 5]),  # for with continue
        ],
    )
    def test_loop_control_statements(self, loop_type, control, expected_result):
        """Test break and continue in different loop types."""
        if loop_type == "while":
            if control == "break":
                code = """
i = 0
result = []
while i < 10:
    i = i + 1
    if i == 3:
        break
    result.append(i)
"""
            else:  # continue
                code = """
i = 0
result = []
while i < 5:
    i = i + 1
    if i == 3:
        continue
    result.append(i)
"""
        else:  # for loop
            if control == "break":
                code = """
result = []
for i in [1, 2, 3, 4, 5]:
    if i == 4:
        break
    result.append(i)
"""
            else:  # continue
                code = """
result = []
for i in [1, 2, 3, 4, 5]:
    if i == 3:
        continue
    result.append(i)
"""

        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == expected_result

    @pytest.mark.parametrize(
        "has_break,expected",
        [
            (False, [1, 2, 3, "completed"]),  # no break, else executes
            (True, [1, 2, 3]),  # break occurs, else skipped
        ],
    )
    def test_for_loop_with_else(self, has_break, expected):
        """Test for loop with else clause."""
        if has_break:
            code = """
result = []
for i in [1, 2, 3, 4, 5]:
    result.append(i)
    if i == 3:
        break
else:
    result.append("completed")
"""
        else:
            code = """
result = []
for i in [1, 2, 3]:
    result.append(i)
else:
    result.append("completed")
"""

        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == expected

    def test_nested_loops_with_break(self):
        """Test that break only affects inner loop."""
        code = """
result = []
for i in [1, 2]:
    for j in [1, 2, 3]:
        if j == 2:
            break
        result.append((i, j))
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == [(1, 1), (2, 1)]


class TestAssert:
    """Test assert statements."""

    @pytest.mark.parametrize(
        "assertion,should_pass",
        [
            ("assert True", True),
            ("assert 5 > 3", True),
            ("assert 1 == 1", True),
            ("assert False", False),
            ("assert 3 > 5", False),
            ("assert 1 == 2", False),
        ],
    )
    def test_basic_assertions(self, assertion, should_pass):
        """Test basic assert statements."""
        interpreter = SiluInterpreter()
        tree = ast.parse(assertion)

        if should_pass:
            interpreter.visit(tree)  # Should not raise
        else:
            with pytest.raises(AssertionError):
                interpreter.visit(tree)

    def test_assert_with_message(self):
        """Test assert with custom message."""
        code = 'assert False, "This should fail"'
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(AssertionError, match="This should fail"):
            interpreter.visit(tree)

    def test_assert_with_variables_and_expressions(self):
        """Test assert with variables and complex expressions."""
        code = """
x = 10
numbers = [1, 2, 3]
assert x == 10, "x should be 10"
assert len(numbers) == 3 and numbers[0] == 1
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)  # Should not raise


class TestAnnotatedAssignment:
    """Test annotated assignments."""

    @pytest.mark.parametrize(
        "code,var_name,expected_value",
        [
            ("x: int = 5", "x", 5),
            ("name: str = 'Alice'", "name", "Alice"),
            ("height: float = 5.6", "height", 5.6),
            ("is_student: bool = True", "is_student", True),
        ],
    )
    def test_annotated_assignments(self, code, var_name, expected_value):
        """Test annotated assignments with different types."""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get(var_name) == expected_value

    def test_annotated_assignment_without_value(self):
        """Test annotated assignment without initial value."""
        code = "future_value: int"
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)  # Should not raise

        # Variable should not be set
        with pytest.raises(NameError):
            interpreter.env.get("future_value")

    def test_annotated_assignment_complex_types(self):
        """Test annotated assignment with complex types."""
        code = """
items: list = [1, 2, 3]
mapping: dict = {"key": "value"}
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("items") == [1, 2, 3]
        assert interpreter.env.get("mapping") == {"key": "value"}


class TestLambda:
    """Test lambda functions."""

    @pytest.mark.parametrize(
        "code,expected_result",
        [
            ("add = lambda a, b: a + b\nresult = add(3, 5)", 8),
            ("square = lambda x: x * x\nresult = square(4)", 16),
            ("get_answer = lambda: 42\nresult = get_answer()", 42),
            ("result = (lambda x: x * 2)(7)", 14),  # immediate call
        ],
    )
    def test_basic_lambda_functions(self, code, expected_result):
        """Test basic lambda function operations."""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == expected_result

    def test_lambda_in_data_structures(self):
        """Test lambda functions in lists and complex usage."""
        code = """
operations = [
    lambda x: x + 1,
    lambda x: x * 2,
    lambda x: x - 3
]
value = 5
for op in operations:
    value = op(value)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        # 5 -> 6 -> 12 -> 9
        assert interpreter.env.get("value") == 9

    def test_lambda_with_closure(self):
        """Test lambda with closure over outer variables."""
        code = """
def make_multiplier(factor):
    return lambda x: x * factor

double = make_multiplier(2)
triple = make_multiplier(3)
result1 = double(5)
result2 = triple(4)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result1") == 10
        assert interpreter.env.get("result2") == 12

    def test_lambda_error_handling(self):
        """Test lambda error cases."""
        code = """
add = lambda a, b: a + b
result = add(1)  # Missing second argument
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(
            TypeError, match="Lambda takes 2 arguments but 1 were given"
        ):
            interpreter.visit(tree)

    def test_lambda_complex_expressions(self):
        """Test lambda with complex body expressions."""
        code = """
condition_check = lambda x: x > 0 and x < 100
result1 = condition_check(50)
result2 = condition_check(-5)
result3 = condition_check(150)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result1") is True
        assert interpreter.env.get("result2") is False
        assert interpreter.env.get("result3") is False


class TestCombinedFeatures:
    """Test combinations of new features."""

    def test_lambda_with_assert(self):
        """Test lambda function with assert."""
        code = """
safe_divide = lambda a, b: a / b
result = safe_divide(10, 2)
assert result == 5.0
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 5.0

    def test_comprehensive_feature_integration(self):
        """Test function using multiple new features together."""
        code = """
def process_numbers(numbers):
    is_valid = lambda n: isinstance(n, int) and n > 0
    result: list = []

    for num in numbers:
        if not is_valid(num):
            continue
        if num > 100:
            break
        result.append(num * 2)

    assert isinstance(result, list)
    return result

test_data = [1, 2, -3, 4, 5, 101, 6]
filtered = process_numbers(test_data)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        # Process: 1->2, 2->4, skip -3, 4->8, 5->10, break at 101
        assert interpreter.env.get("filtered") == [2, 4, 8, 10]

    def test_loop_with_lambda_and_control_flow(self):
        """Test loop with lambda and break/continue statements."""
        code = """
is_even = lambda n: n % 2 == 0
result = []
for num in [1, 2, 3, 4, 5, 6, 7, 8]:
    if num > 6:
        break
    if is_even(num):
        result.append(num)
    else:
        continue
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == [2, 4, 6]
