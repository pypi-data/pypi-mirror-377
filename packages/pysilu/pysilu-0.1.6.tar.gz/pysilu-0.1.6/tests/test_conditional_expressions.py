"""
Test conditional expressions (ternary operator) support.

Tests for the if-else expression syntax: value_if_true if condition else value_if_false
"""

import ast
from silu.interpreter import SiluInterpreter
from silu.ir_generator import SiluIRGenerator
from silu.ir_interpreter import IRInterpreter


class TestConditionalExpressions:
    """Test conditional expressions in the main interpreter."""

    def test_basic_conditional_expression(self):
        """Test basic conditional expression."""
        interpreter = SiluInterpreter()
        code = """
result1 = 1 if True else 2
result2 = 1 if False else 2
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result1") == 1
        assert interpreter.env.get("result2") == 2

    def test_conditional_with_variables(self):
        """Test conditional expression with variables."""
        interpreter = SiluInterpreter()
        code = """
x = 5
y = 10
result = x if x > y else y
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 10

    def test_conditional_with_complex_expressions(self):
        """Test conditional expression with complex expressions."""
        interpreter = SiluInterpreter()
        code = """
a = 3
b = 7
result = (a * 2) if (a + b) > 5 else (b - a)
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 6  # a * 2

    def test_nested_conditional_expressions(self):
        """Test nested conditional expressions."""
        interpreter = SiluInterpreter()
        code = """
x = 1
result = "small" if x < 5 else ("medium" if x < 10 else "large")
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == "small"

    def test_conditional_in_function_return(self):
        """Test conditional expression in function return."""
        interpreter = SiluInterpreter()
        code = """
def abs_value(n):
    return n if n >= 0 else -n

result1 = abs_value(5)
result2 = abs_value(-3)
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result1") == 5
        assert interpreter.env.get("result2") == 3

    def test_conditional_with_different_types(self):
        """Test conditional expression with different value types."""
        interpreter = SiluInterpreter()
        code = """
condition = True
result1 = 42 if condition else "hello"
result2 = [1, 2, 3] if not condition else {"key": "value"}
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result1") == 42
        assert interpreter.env.get("result2") == {"key": "value"}

    def test_conditional_with_truthiness(self):
        """Test conditional expression with truthy/falsy values."""
        interpreter = SiluInterpreter()
        code = """
empty_list = []
non_empty_list = [1, 2, 3]
result1 = "has items" if empty_list else "empty"
result2 = "has items" if non_empty_list else "empty"
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result1") == "empty"
        assert interpreter.env.get("result2") == "has items"

    def test_conditional_in_print(self):
        """Test conditional expression in print statement."""
        interpreter = SiluInterpreter()
        code = """
age = 15
print("adult" if age >= 18 else "minor")
"""
        tree = ast.parse(code)
        # We can't easily test print output, but we can make sure it doesn't crash
        interpreter.visit(tree)  # Should not raise an exception


class TestConditionalExpressionsIR:
    """Test conditional expressions in the IR system."""

    def test_ir_generation_for_conditional(self):
        """Test IR generation for conditional expressions."""
        generator = SiluIRGenerator()
        code = """
result = 1 if True else 2
"""
        tree = ast.parse(code)
        ir = generator.visit(tree)

        # Check that the IR contains an if_expr node
        assert ir[0] == "module"
        statements = ir[1]
        assign_stmt = statements[0]
        assert assign_stmt[0] == "assign"

        # The value should be an if_expr
        if_expr_ir = assign_stmt[2]
        assert if_expr_ir[0] == "if_expr"

    def test_ir_execution_basic(self):
        """Test IR execution of basic conditional expression."""
        # Generate IR
        generator = SiluIRGenerator()
        code = """
result1 = 42 if True else 0
result2 = 0 if False else 99
"""
        tree = ast.parse(code)
        ir = generator.visit(tree)

        # Execute IR
        interpreter = IRInterpreter()
        interpreter.execute_program(ir)

        assert interpreter._get_variable("result1") == 42
        assert interpreter._get_variable("result2") == 99

    def test_ir_execution_with_variables(self):
        """Test IR execution of conditional with variables."""
        generator = SiluIRGenerator()
        code = """
x = 10
y = 5
max_val = x if x > y else y
"""
        tree = ast.parse(code)
        ir = generator.visit(tree)

        interpreter = IRInterpreter()
        interpreter.execute_program(ir)

        assert interpreter._get_variable("max_val") == 10

    def test_ir_execution_in_function(self):
        """Test IR execution of conditional in function."""
        generator = SiluIRGenerator()
        code = """
def sign(n):
    return 1 if n > 0 else (-1 if n < 0 else 0)

result = sign(-5)
"""
        tree = ast.parse(code)
        ir = generator.visit(tree)

        interpreter = IRInterpreter()
        interpreter.execute_program(ir)

        assert interpreter._get_variable("result") == -1

    def test_ir_execution_nested_conditional(self):
        """Test IR execution of nested conditional expressions."""
        generator = SiluIRGenerator()
        code = """
score = 85
grade = "A" if score >= 90 else ("B" if score >= 80 else ("C" if score >= 70 else "F"))
"""
        tree = ast.parse(code)
        ir = generator.visit(tree)

        interpreter = IRInterpreter()
        interpreter.execute_program(ir)

        assert interpreter._get_variable("grade") == "B"


class TestConditionalExpressionsEdgeCases:
    """Test edge cases and error conditions for conditional expressions."""

    def test_conditional_with_none_values(self):
        """Test conditional expression with None values."""
        interpreter = SiluInterpreter()
        code = """
result1 = None if True else "not none"
result2 = "not none" if False else None
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result1") is None
        assert interpreter.env.get("result2") is None

    def test_conditional_short_circuiting(self):
        """Test that conditional expressions properly short-circuit."""
        interpreter = SiluInterpreter()
        code = """
# This should not cause an error even though division by zero would fail
# because the condition is False, so the first expression is not evaluated
x = 0
result = (10 / x) if False else "safe"
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == "safe"

    def test_conditional_with_function_calls(self):
        """Test conditional expressions with function calls."""
        interpreter = SiluInterpreter()
        code = """
def get_positive():
    return 42

def get_negative():
    return -42

condition = True
result = get_positive() if condition else get_negative()
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 42

    def test_multiple_conditionals_in_expression(self):
        """Test multiple conditional expressions in the same statement."""
        interpreter = SiluInterpreter()
        code = """
a = True
b = False
result = (1 if a else 2) + (3 if b else 4)
"""
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 5  # 1 + 4
