"""
Tests for the IR to source converter module.
"""

import pytest
import tempfile
import os
from silu.ir_to_source import (
    IRToSourceConverter,
    convert_ir_file_to_source,
    convert_ir_string_to_source,
    make_expression_readable,
    simplify_value_display,
)


class TestIRToSourceConverter:
    """Test cases for the IRToSourceConverter class."""

    def test_convert_literal_values(self):
        """Test conversion of literal values."""
        converter = IRToSourceConverter()

        assert converter.convert_to_source(42) == "42"
        assert converter.convert_to_source(3.14) == "3.14"
        assert converter.convert_to_source("hello world") == "'hello world'"
        assert converter.convert_to_source(True) == "True"
        assert converter.convert_to_source(False) == "False"
        assert converter.convert_to_source(None) == "None"

    def test_convert_simple_assignment(self):
        """Test conversion of simple assignment."""
        converter = IRToSourceConverter()
        ir_node = ("assign", "x", 42, None)
        result = converter.convert_to_source(ir_node)
        expected = "x = 42"
        assert result == expected

    def test_convert_tuple_assignment(self):
        """Test conversion of tuple assignment."""
        converter = IRToSourceConverter()

        # Simple tuple assignment
        ir_node = ("tuple_assign", ("a", "b"), ("tuple", (("const", 1), ("const", 2))))
        result = converter.convert_to_source(ir_node)
        expected = "a, b = (1, 2)"
        assert result == expected

        # Three variable tuple assignment
        ir_node = (
            "tuple_assign",
            ("x", "y", "z"),
            ("tuple", (("const", 10), ("const", 20), ("const", 30))),
        )
        result = converter.convert_to_source(ir_node)
        expected = "x, y, z = (10, 20, 30)"
        assert result == expected

        # Tuple assignment with variables
        ir_node = (
            "tuple_assign",
            ("a", "b"),
            ("tuple", (("name", "b"), ("+", ("name", "a"), ("name", "b")))),
        )
        result = converter.convert_to_source(ir_node)
        expected = "a, b = (b, a + b)"
        assert result == expected

    def test_convert_multiple_assignment(self):
        """Test conversion of multiple assignment."""
        converter = IRToSourceConverter()

        # Simple multiple assignment: a = b = 1
        ir_node = (
            "multi_assign",
            (("assign", "a", ("const", 1), None), ("assign", "b", ("const", 1), None)),
        )
        result = converter.convert_to_source(ir_node)
        expected = "a = b = 1"
        assert result == expected

        # Three variable multiple assignment: x = y = z = 42
        ir_node = (
            "multi_assign",
            (
                ("assign", "x", ("const", 42), None),
                ("assign", "y", ("const", 42), None),
                ("assign", "z", ("const", 42), None),
            ),
        )
        result = converter.convert_to_source(ir_node)
        expected = "x = y = z = 42"
        assert result == expected

        # Multiple assignment with expression: a = b = 2 + 3
        ir_node = (
            "multi_assign",
            (
                ("assign", "a", ("+", ("const", 2), ("const", 3)), None),
                ("assign", "b", ("+", ("const", 2), ("const", 3)), None),
            ),
        )
        result = converter.convert_to_source(ir_node)
        expected = "a = b = 2 + 3"
        assert result == expected

    def test_convert_binary_operations(self):
        """Test conversion of binary operations."""
        converter = IRToSourceConverter()

        # Addition
        ir_node = ("+", 5, 3)
        result = converter.convert_to_source(ir_node)
        expected = "5 + 3"
        assert result == expected

        # Multiplication
        ir_node = ("*", 4, 6)
        result = converter.convert_to_source(ir_node)
        expected = "4 * 6"
        assert result == expected

        # Nested operations
        ir_node = ("+", ("*", 2, 3), 4)
        result = converter.convert_to_source(ir_node)
        expected = "2 * 3 + 4"
        assert result == expected

    def test_convert_comparison_operations(self):
        """Test conversion of comparison operations."""
        converter = IRToSourceConverter()

        ir_node = ("<", "x", 10)
        result = converter.convert_to_source(ir_node)
        expected = "x < 10"
        assert result == expected

        ir_node = ("==", "y", 5)
        result = converter.convert_to_source(ir_node)
        expected = "y == 5"
        assert result == expected

    def test_convert_chained_comparison(self):
        """Test conversion of chained comparisons."""
        converter = IRToSourceConverter()

        ir_node = ("chained_compare", (("<", 1, "x"), ("<", "x", 10)))
        result = converter.convert_to_source(ir_node)
        expected = "1 < x < 10"
        assert result == expected

    def test_convert_boolean_operations(self):
        """Test conversion of boolean operations."""
        converter = IRToSourceConverter()

        ir_node = ("and", True, False)
        result = converter.convert_to_source(ir_node)
        expected = "True and False"
        assert result == expected

        ir_node = ("or", ("==", "x", 1), ("==", "x", 2))
        result = converter.convert_to_source(ir_node)
        expected = "x == 1 or x == 2"
        assert result == expected

    def test_convert_unary_operations(self):
        """Test conversion of unary operations."""
        converter = IRToSourceConverter()

        ir_node = ("-", 5)
        result = converter.convert_to_source(ir_node)
        expected = "-5"
        assert result == expected

        ir_node = ("not", True)
        result = converter.convert_to_source(ir_node)
        expected = "not True"
        assert result == expected

    def test_convert_function_call(self):
        """Test conversion of function calls."""
        converter = IRToSourceConverter()

        # Simple function call
        ir_node = ("call", "print", ("hello world",), ())
        result = converter.convert_to_source(ir_node)
        expected = "print('hello world')"
        assert result == expected

        # Function call with multiple arguments
        ir_node = ("call", "max", (1, 2, 3), ())
        result = converter.convert_to_source(ir_node)
        expected = "max(1, 2, 3)"
        assert result == expected

    def test_convert_list(self):
        """Test conversion of lists."""
        converter = IRToSourceConverter()

        ir_node = ("list", (1, 2, 3))
        result = converter.convert_to_source(ir_node)
        expected = "[1, 2, 3]"
        assert result == expected

        # Empty list
        ir_node = ("list", ())
        result = converter.convert_to_source(ir_node)
        expected = "[]"
        assert result == expected

    def test_convert_tuple(self):
        """Test conversion of tuples."""
        converter = IRToSourceConverter()

        ir_node = ("tuple", (1, 2, 3))
        result = converter.convert_to_source(ir_node)
        expected = "(1, 2, 3)"
        assert result == expected

        # Single element tuple
        ir_node = ("tuple", (1,))
        result = converter.convert_to_source(ir_node)
        expected = "(1,)"
        assert result == expected

    def test_convert_dict(self):
        """Test conversion of dictionaries."""
        converter = IRToSourceConverter()

        ir_node = ("dict", (("key1", "value1"), ("key2", "value2")))
        result = converter.convert_to_source(ir_node)
        expected = "{'key1': 'value1', 'key2': 'value2'}"
        assert result == expected

    def test_convert_subscript(self):
        """Test conversion of subscript operations."""
        converter = IRToSourceConverter()

        ir_node = ("subscript", "arr", 0)
        result = converter.convert_to_source(ir_node)
        expected = "arr[0]"
        assert result == expected

    def test_convert_subscript_assignment(self):
        """Test conversion of subscript assignments."""
        converter = IRToSourceConverter()

        ir_node = ("subscript_assign", "arr", 0, 42)
        result = converter.convert_to_source(ir_node)
        expected = "arr[0] = 42"
        assert result == expected

    def test_convert_if_statement(self):
        """Test conversion of if statements."""
        converter = IRToSourceConverter()

        # Simple if
        ir_node = ("if", ("==", "x", 5), (("assign", "y", 10, None),), ())
        result = converter.convert_to_source(ir_node)
        expected = "if x == 5:\n    y = 10"
        assert result == expected

        # If-else
        ir_node = (
            "if",
            ("<", "x", 0),
            (("assign", "y", -1, None),),
            (("assign", "y", 1, None),),
        )
        result = converter.convert_to_source(ir_node)
        expected = "if x < 0:\n    y = -1\nelse:\n    y = 1"
        assert result == expected

    def test_convert_while_loop(self):
        """Test conversion of while loops."""
        converter = IRToSourceConverter()

        ir_node = ("while", (">", "x", 0), (("assign", "x", ("-", "x", 1), None),))
        result = converter.convert_to_source(ir_node)
        expected = "while x > 0:\n    x = x - 1"
        assert result == expected

    def test_convert_for_loop(self):
        """Test conversion of for loops."""
        converter = IRToSourceConverter()

        ir_node = (
            "for",
            "i",
            ("list", (1, 2, 3)),
            (("call", "print", ("i",), ()),),
            (),
        )
        result = converter.convert_to_source(ir_node)
        expected = "for i in [1, 2, 3]:\n    print(i)"
        assert result == expected

    def test_convert_function_definition(self):
        """Test conversion of function definitions."""
        converter = IRToSourceConverter()

        ir_node = ("func_def", "add", ("a", "b"), (("return", ("+", "a", "b")),))
        result = converter.convert_to_source(ir_node)
        expected = "def add(a, b):\n    return a + b"
        assert result == expected

    def test_convert_return_statement(self):
        """Test conversion of return statements."""
        converter = IRToSourceConverter()

        # Return with value
        ir_node = ("return", 42)
        result = converter.convert_to_source(ir_node)
        expected = "return 42"
        assert result == expected

        # Return without value
        ir_node = ("return", None)
        result = converter.convert_to_source(ir_node)
        expected = "return"
        assert result == expected

    def test_convert_module(self):
        """Test conversion of entire modules."""
        converter = IRToSourceConverter()

        ir_node = (
            "module",
            (
                ("assign", "x", 5, None),
                ("assign", "y", 10, None),
                ("assign", "z", ("+", "x", "y"), None),
            ),
        )
        result = converter.convert_to_source(ir_node)
        expected = "x = 5\ny = 10\nz = x + y"
        assert result == expected

    def test_operator_precedence(self):
        """Test that operator precedence is handled correctly."""
        converter = IRToSourceConverter()

        # Should not need parentheses: 2 + 3 * 4
        ir_node = ("+", 2, ("*", 3, 4))
        result = converter.convert_to_source(ir_node)
        expected = "2 + 3 * 4"
        assert result == expected

        # Should need parentheses: (2 + 3) * 4
        ir_node = ("*", ("+", 2, 3), 4)
        result = converter.convert_to_source(ir_node)
        expected = "(2 + 3) * 4"
        assert result == expected

    def test_indentation(self):
        """Test proper indentation handling."""
        converter = IRToSourceConverter(indent_size=2)

        ir_node = ("if", True, (("if", False, (("assign", "x", 1, None),), ()),), ())
        result = converter.convert_to_source(ir_node)
        expected = "if True:\n  if False:\n    x = 1"
        assert result == expected


class TestConvenienceFunctions:
    """Test the convenience functions."""

    def test_convert_ir_string_to_source(self):
        """Test converting IR string to source code."""
        # Python literal format
        ir_string = '("assign", "x", 42, None)'
        result = convert_ir_string_to_source(ir_string)
        expected = "x = 42"
        assert result == expected

        # JSON format
        ir_string = '["assign", "x", 42, null]'
        result = convert_ir_string_to_source(ir_string)
        expected = "x = 42"
        assert result == expected

    def test_convert_ir_file_to_source(self):
        """Test converting IR file to source code."""
        # Create temporary IR file
        ir_content = (
            '["module", [["assign", "x", 42, null], ["assign", "y", "hello", null]]]'
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ir.json", delete=False
        ) as f:
            f.write(ir_content)
            ir_file_path = f.name

        try:
            # Convert without output file
            result = convert_ir_file_to_source(ir_file_path)
            expected = "x = 42\ny = 'hello'"
            assert result == expected

            # Convert with output file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".si", delete=False) as f:
                output_file_path = f.name

            try:
                result = convert_ir_file_to_source(ir_file_path, output_file_path)

                # Check that file was written
                with open(output_file_path, "r") as f:
                    file_content = f.read().strip()
                assert file_content == expected

            finally:
                os.unlink(output_file_path)

        finally:
            os.unlink(ir_file_path)

    def test_make_expression_readable(self):
        """Test the shared expression conversion function."""
        expr = ("+", ("*", 2, 3), 4)
        result = make_expression_readable(expr)
        expected = "2 * 3 + 4"
        assert result == expected

    def test_simplify_value_display(self):
        """Test the shared value simplification function."""
        value = ("call", "print", ("hello world",), ())
        result = simplify_value_display(value)
        expected = "print('hello world')"
        assert result == expected

    def test_invalid_ir_format(self):
        """Test handling of invalid IR formats."""
        with pytest.raises(ValueError):
            convert_ir_string_to_source("invalid ir format")

        # Create temporary file with invalid content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ir", delete=False) as f:
            f.write("invalid content")
            invalid_file_path = f.name

        try:
            with pytest.raises(ValueError):
                convert_ir_file_to_source(invalid_file_path)
        finally:
            os.unlink(invalid_file_path)


class TestComplexExamples:
    """Test complex real-world examples."""

    def test_fibonacci_function(self):
        """Test conversion of a Fibonacci function."""
        converter = IRToSourceConverter()

        ir_node = (
            "module",
            (
                (
                    "func_def",
                    "fibonacci",
                    ("n",),
                    (
                        (
                            "if",
                            ("<=", "n", 1),
                            (("return", "n"),),
                            (
                                (
                                    "return",
                                    (
                                        "+",
                                        ("call", "fibonacci", (("-", "n", 1),), ()),
                                        ("call", "fibonacci", (("-", "n", 2),), ()),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                ("assign", "result", ("call", "fibonacci", (10,), ()), None),
                ("call", "print", ("result",), ()),
            ),
        )

        result = converter.convert_to_source(ir_node)

        expected_lines = [
            "def fibonacci(n):",
            "    if n <= 1:",
            "        return n",
            "    else:",
            "        return fibonacci(n - 1) + fibonacci(n - 2)",
            "result = fibonacci(10)",
            "print(result)",
        ]
        expected = "\n".join(expected_lines)

        assert result == expected

    def test_nested_data_structures(self):
        """Test conversion involving nested data structures."""
        converter = IRToSourceConverter()

        ir_node = (
            "module",
            (
                (
                    "assign",
                    "data",
                    (
                        "dict",
                        (
                            (
                                "users",
                                (
                                    "list",
                                    (
                                        ("dict", (("name", "Alice"), ("age", 30))),
                                        ("dict", (("name", "Bob"), ("age", 25))),
                                    ),
                                ),
                            ),
                            ("settings", ("dict", (("theme", "dark"), ("lang", "en")))),
                        ),
                    ),
                    None,
                ),
                (
                    "assign",
                    "first_user",
                    ("subscript", ("subscript", "data", "users"), 0),
                    None,
                ),
                ("call", "print", (("subscript", "first_user", "name"),), ()),
            ),
        )

        result = converter.convert_to_source(ir_node)

        expected_lines = [
            "data = {'users': [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}], 'settings': {'theme': 'dark', 'lang': 'en'}}",
            "first_user = data['users'][0]",
            "print(first_user['name'])",
        ]
        expected = "\n".join(expected_lines)

        assert result == expected
