#!/usr/bin/env python3
"""
Tests for the IR Common module.

This module tests the shared IR processing utilities in ir_common.py.
"""

import unittest

from silu.ir_common import (
    IRProcessingError,
    dispatch_ir_node,
    create_handlers_map,
    log_ir_processing,
    handle_node_error,
    validate_node_args,
    process_ir_block,
    extract_names_from_params,
    process_const_node,
    is_valid_identifier,
)


class TestIRNodeDispatching(unittest.TestCase):
    """Test IR node dispatching functionality."""

    def test_dispatch_ir_node(self):
        """Test dispatching an IR node to the appropriate handler."""
        # Setup test handlers
        handlers = {
            "const": lambda node: node[1],
            "name": lambda node: f"var:{node[1]}",
            "binary_op": lambda node: f"{node[1]} {node[2]} {node[3]}",
        }

        # Test successful dispatching
        result = dispatch_ir_node(("const", 42), handlers)
        self.assertEqual(result, 42)

        result = dispatch_ir_node(("name", "x"), handlers)
        self.assertEqual(result, "var:x")

        result = dispatch_ir_node(("binary_op", "a", "+", "b"), handlers)
        self.assertEqual(result, "a + b")

        # Test with default handler
        # default_handler = lambda node: f"default:{node[0]}"
        def default_handler(node):
            return f"default:{node[0]}"

        result = dispatch_ir_node(("unknown", 123), handlers, default_handler)
        self.assertEqual(result, "default:unknown")

        # Test invalid node
        with self.assertRaises(IRProcessingError):
            dispatch_ir_node("not_a_node", handlers)

        # Test missing handler with no default
        with self.assertRaises(IRProcessingError):
            dispatch_ir_node(("unknown", 123), handlers)

    def test_create_handlers_map(self):
        """Test creating a handlers map from methods of an object."""

        # Setup test class with handler methods
        class TestProcessor:
            def _process_const(self, node):
                return node[1]

            def _process_name(self, node):
                return f"var:{node[1]}"

            def non_handler_method(self):
                return "not a handler"

        processor = TestProcessor()

        # Create handlers map
        handlers = create_handlers_map(processor)

        # Check if handlers were correctly mapped
        self.assertIn("const", handlers)
        self.assertIn("name", handlers)
        self.assertNotIn("non_handler_method", handlers)

        # Test the mapped handlers
        self.assertEqual(handlers["const"](("const", 42)), 42)
        self.assertEqual(handlers["name"](("name", "x")), "var:x")


def test_log_ir_processing(capsys):
    """Test logging IR node processing."""
    # Test basic logging
    log_ir_processing("const", [42], "INFO")
    captured = capsys.readouterr()
    assert "[INFO] Processing const: 42" in captured.err

    # Test with multiple arguments
    log_ir_processing("binary_op", ["a", "+", "b"], "DEBUG")
    captured = capsys.readouterr()
    assert "[DEBUG] Processing binary_op: 'a', '+', 'b'" in captured.err

    # Test with extra info
    log_ir_processing("call", ["print", ["Hello"]], "WARNING", {"line": 10})
    captured = capsys.readouterr()
    assert "[WARNING] Processing call:" in captured.err
    assert "| {'line': 10}" in captured.err

    # Test with long lists that get summarized
    log_ir_processing("module", [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], "INFO")
    captured = capsys.readouterr()
    assert "list[10 items]" in captured.err


class TestErrorHandling(unittest.TestCase):
    """Test error handling functionality."""

    def test_handle_node_error(self):
        """Test handling an error during node processing."""
        # Test with raising the error
        node = ("const", 42)
        error = ValueError("Test error")

        with self.assertRaises(IRProcessingError) as context:
            handle_node_error(node, error, "test context", raise_error=True)

        self.assertIn("Error processing const node", str(context.exception))
        self.assertIn("Test error", str(context.exception))
        self.assertIn("test context", str(context.exception))

        # Test without raising the error
        error_message = handle_node_error(
            node, error, "test context", raise_error=False
        )
        self.assertIn("Error processing const node", error_message)
        self.assertIn("Test error", error_message)
        self.assertIn("test context", error_message)


class TestNodeValidation(unittest.TestCase):
    """Test node validation functionality."""

    def test_validate_node_args(self):
        """Test validating IR node arguments."""
        # Valid node
        validate_node_args(("const", 42), "const", 1, 1)

        # Invalid format
        with self.assertRaises(IRProcessingError):
            validate_node_args("not_a_node", "const")

        # Wrong opcode
        with self.assertRaises(IRProcessingError):
            validate_node_args(("name", "x"), "const")

        # Too few arguments
        with self.assertRaises(IRProcessingError):
            validate_node_args(("binary_op", "a"), "binary_op", 3, 3)

        # Too many arguments
        with self.assertRaises(IRProcessingError):
            validate_node_args(("const", 42, "extra"), "const", 1, 1)


class TestCommonNodeProcessing(unittest.TestCase):
    """Test common node processing functionality."""

    def test_process_ir_block(self):
        """Test processing a block of IR statements."""
        # Setup test statements and processing function
        statements = [
            ("const", 1),
            ("const", 2),
            ("return", 3),
            ("const", 4),
        ]

        def process_func(node):
            return node[1]

        # Test without breaking on return
        results = process_ir_block(statements, process_func, break_on_return=False)
        self.assertEqual(results, [1, 2, 3, 4])

        # Test with breaking on return
        results = process_ir_block(statements, process_func, break_on_return=True)
        self.assertEqual(results, [1, 2, 3])

    def test_extract_names_from_params(self):
        """Test extracting parameter names from function parameters."""
        # Simple parameter names
        params = ["a", "b", "c"]
        names = extract_names_from_params(params)
        self.assertEqual(names, ["a", "b", "c"])

        # With tuple unpacking
        params = ["a", ("tuple_unpack", ["b", "c"]), "d"]
        names = extract_names_from_params(params)
        self.assertEqual(names, ["a", "b", "c", "d"])

        # Invalid parameter format
        with self.assertRaises(IRProcessingError):
            extract_names_from_params(["a", ("invalid", "b"), "c"])

    def test_process_const_node(self):
        """Test processing a constant node."""
        # Valid constant node
        value = process_const_node(("const", 42))
        self.assertEqual(value, 42)

        # Invalid node format
        with self.assertRaises(IRProcessingError):
            process_const_node("not_a_node")

        # Wrong opcode
        with self.assertRaises(IRProcessingError):
            process_const_node(("name", "x"))

        # Wrong number of arguments
        with self.assertRaises(IRProcessingError):
            process_const_node(("const", 42, "extra"))

    def test_is_valid_identifier(self):
        """Test checking if a string is a valid Python identifier."""
        # Valid identifiers
        self.assertTrue(is_valid_identifier("x"))
        self.assertTrue(is_valid_identifier("variable_name"))
        self.assertTrue(is_valid_identifier("_private"))
        self.assertTrue(is_valid_identifier("name123"))

        # Invalid identifiers
        self.assertFalse(is_valid_identifier(""))
        self.assertFalse(is_valid_identifier("123name"))
        self.assertFalse(is_valid_identifier("name-with-dashes"))
        self.assertFalse(is_valid_identifier("name with spaces"))
        self.assertFalse(is_valid_identifier("for"))  # Python keyword


if __name__ == "__main__":
    unittest.main()
