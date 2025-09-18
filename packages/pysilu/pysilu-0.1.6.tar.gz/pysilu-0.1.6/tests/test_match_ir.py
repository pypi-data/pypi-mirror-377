"""
Tests for Match Statement IR Generation

This module tests the IR generation for Python's match-case statements
(structural pattern matching) introduced in Python 3.10.
"""

import ast
from silu.ir_generator import SiluIRGenerator


class TestMatchIRGeneration:
    """Test IR generation for match statements."""

    def test_basic_match_value_patterns(self):
        """Test basic match with value patterns."""
        code = """
match x:
    case 1:
        print("one")
    case 2:
        print("two")
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        # Extract the match statement
        match_stmt = ir[1][0]  # First statement in module
        assert match_stmt[0] == "match"
        assert match_stmt[1] == ("name", "x")  # Subject

        # Check cases
        cases = match_stmt[2]
        assert len(cases) == 2

        # First case: case 1
        case1 = cases[0]
        assert case1[0] == "match_case"
        assert case1[1] == ("match_value", ("const", 1))  # Pattern
        assert case1[2] is None  # No guard
        assert len(case1[3]) == 1  # Body has one statement

        # Second case: case 2
        case2 = cases[1]
        assert case2[0] == "match_case"
        assert case2[1] == ("match_value", ("const", 2))  # Pattern
        assert case2[2] is None  # No guard
        assert len(case2[3]) == 1  # Body has one statement

    def test_match_or_patterns(self):
        """Test match with or patterns."""
        code = """
match x:
    case 1 | 2 | 3:
        print("small")
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]
        case = cases[0]

        # Check or pattern
        pattern = case[1]
        assert pattern[0] == "match_or"
        or_patterns = pattern[1]
        assert len(or_patterns) == 3
        assert or_patterns[0] == ("match_value", ("const", 1))
        assert or_patterns[1] == ("match_value", ("const", 2))
        assert or_patterns[2] == ("match_value", ("const", 3))

    def test_match_sequence_patterns(self):
        """Test match with sequence patterns."""
        code = """
match x:
    case [1, 2, y]:
        print(y)
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]
        case = cases[0]

        # Check sequence pattern
        pattern = case[1]
        assert pattern[0] == "match_sequence"
        seq_patterns = pattern[1]
        assert len(seq_patterns) == 3
        assert seq_patterns[0] == ("match_value", ("const", 1))
        assert seq_patterns[1] == ("match_value", ("const", 2))
        assert seq_patterns[2] == ("match_as", None, "y")  # Capture pattern

    def test_match_mapping_patterns(self):
        """Test match with mapping patterns."""
        code = """
match x:
    case {"name": n, "age": a}:
        print(n, a)
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]
        case = cases[0]

        # Check mapping pattern
        pattern = case[1]
        assert pattern[0] == "match_mapping"
        keys = pattern[1]
        patterns = pattern[2]
        rest = pattern[3]

        assert len(keys) == 2
        assert keys[0] == ("const", "name")
        assert keys[1] == ("const", "age")

        assert len(patterns) == 2
        assert patterns[0] == ("match_as", None, "n")
        assert patterns[1] == ("match_as", None, "a")

        assert rest is None

    def test_match_as_patterns(self):
        """Test match with as patterns (capture and wildcard)."""
        code = """
match x:
    case y:
        print(y)
    case _:
        print("default")
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]

        # First case: capture pattern
        case1 = cases[0]
        pattern1 = case1[1]
        assert pattern1[0] == "match_as"
        assert pattern1[1] is None  # No nested pattern
        assert pattern1[2] == "y"  # Capture name

        # Second case: wildcard pattern
        case2 = cases[1]
        pattern2 = case2[1]
        assert pattern2[0] == "match_as"
        assert pattern2[1] is None  # No nested pattern
        assert pattern2[2] is None  # No capture name (wildcard)

    def test_match_guard_patterns(self):
        """Test match with guard conditions."""
        code = """
match x:
    case n if n > 10:
        print("big")
    case n if n < 0:
        print("negative")
    case n:
        print("other")
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]

        # First case: with guard
        case1 = cases[0]
        assert case1[1] == ("match_as", None, "n")  # Pattern
        assert case1[2] == (">", ("name", "n"), ("const", 10))  # Guard

        # Second case: with guard
        case2 = cases[1]
        assert case2[1] == ("match_as", None, "n")  # Pattern
        assert case2[2] == ("<", ("name", "n"), ("const", 0))  # Guard

        # Third case: no guard
        case3 = cases[2]
        assert case3[1] == ("match_as", None, "n")  # Pattern
        assert case3[2] is None  # No guard

    def test_match_star_patterns(self):
        """Test match with star patterns."""
        code = """
match x:
    case [first, *rest]:
        print(first, rest)
    case [*items]:
        print(items)
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]

        # First case: [first, *rest]
        case1 = cases[0]
        pattern1 = case1[1]
        assert pattern1[0] == "match_sequence"
        seq_patterns1 = pattern1[1]
        assert len(seq_patterns1) == 2
        assert seq_patterns1[0] == ("match_as", None, "first")
        assert seq_patterns1[1] == ("match_star", "rest")

        # Second case: [*items]
        case2 = cases[1]
        pattern2 = case2[1]
        assert pattern2[0] == "match_sequence"
        seq_patterns2 = pattern2[1]
        assert len(seq_patterns2) == 1
        assert seq_patterns2[0] == ("match_star", "items")

    def test_match_complex_nested(self):
        """Test complex nested match patterns."""
        code = """
match data:
    case {"users": [{"name": name, "active": True}]}:
        print(name)
    case {"error": msg} if msg:
        print("Error:", msg)
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]

        # First case: nested mapping and sequence
        case1 = cases[0]
        pattern1 = case1[1]
        assert pattern1[0] == "match_mapping"

        # Check that nested patterns are processed correctly
        # The inner mapping should contain a MatchSingleton for True
        keys = pattern1[1]
        patterns = pattern1[2]
        assert keys[0] == ("const", "users")
        assert patterns[0][0] == "match_sequence"

        # Second case: mapping with guard
        case2 = cases[1]
        pattern2 = case2[1]
        assert pattern2[0] == "match_mapping"
        assert case2[2] == ("name", "msg")  # Guard condition

    def test_match_in_function(self):
        """Test match statement inside a function."""
        code = """
def handle_value(x):
    match x:
        case 0:
            return "zero"
        case n if n > 0:
            return "positive"
        case _:
            return "negative"
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        # Extract function definition
        func_def = ir[1][0]
        assert func_def[0] == "func_def"
        assert func_def[1] == "handle_value"

        # Extract match statement from function body
        func_body = func_def[3]
        match_stmt = func_body[0]
        assert match_stmt[0] == "match"
        assert match_stmt[1] == ("name", "x")

        # Verify all cases are present
        cases = match_stmt[2]
        assert len(cases) == 3

    def test_empty_match_case_body(self):
        """Test match case with empty body (pass statement)."""
        code = """
match x:
    case 1:
        pass
    case 2:
        print("two")
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]

        # First case with pass
        case1 = cases[0]
        body1 = case1[3]
        assert len(body1) == 1
        assert body1[0] == ("pass",)

        # Second case with print
        case2 = cases[1]
        body2 = case2[3]
        assert len(body2) == 1
        assert body2[0][0] == "call"

    def test_match_multiple_statements_in_case(self):
        """Test match case with multiple statements in body."""
        code = """
match x:
    case 1:
        print("found one")
        y = x + 1
        return y
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]
        case = cases[0]
        body = case[3]

        # Should have 3 statements in body
        assert len(body) == 3
        assert body[0][0] == "call"  # print statement
        assert body[1][0] == "assign"  # assignment
        assert body[2][0] == "return"  # return statement

    def test_match_with_constants_and_expressions(self):
        """Test match with various constant types."""
        code = """
match x:
    case True:
        print("boolean true")
    case "hello":
        print("string")
    case 3.14:
        print("float")
    case None:
        print("none")
"""
        tree = ast.parse(code)
        generator = SiluIRGenerator()
        ir = generator.visit(tree)

        match_stmt = ir[1][0]
        cases = match_stmt[2]

        # Check different constant types
        assert cases[0][1] == ("match_singleton", True)
        assert cases[1][1] == ("match_value", ("const", "hello"))
        assert cases[2][1] == ("match_value", ("const", 3.14))
        assert cases[3][1] == ("match_singleton", None)
