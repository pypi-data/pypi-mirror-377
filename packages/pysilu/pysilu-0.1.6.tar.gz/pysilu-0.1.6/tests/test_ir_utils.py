#!/usr/bin/env python3
"""
Tests for IR Utilities Module

Test cases for shared IR processing utilities including parsing,
validation, analysis, and file operations.
"""

import json
import pytest
import tempfile

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from silu.ir_utils import (
    # Parsing functions
    json_to_tuples,
    tuples_to_json_compatible,
    parse_ir_from_json_string,
    parse_ir_from_file,
    # Validation functions
    validate_ir_node_format,
    validate_ir_program,
    validate_ir_node_structure,
    # Analysis functions
    extract_ir_opcodes,
    count_ir_nodes,
    find_ir_nodes_by_opcode,
    # File I/O
    save_ir_to_file,
    safe_ir_parse,
    get_ir_node_info,
    check_file_size,
    # Exceptions
    IRParseError,
    IRValidationError,
    IRConfig,
)


class TestJSONConversion:
    """Test JSON to tuple conversion utilities."""

    def test_json_to_tuples_simple_list(self):
        """Test converting simple list to tuple."""
        input_data = ["const", 42]
        expected = ("const", 42)
        result = json_to_tuples(input_data)
        assert result == expected
        assert isinstance(result, tuple)

    def test_json_to_tuples_nested_structure(self):
        """Test converting nested structure."""
        input_data = ["module", [["const", 1], ["const", 2]]]
        expected = ("module", (("const", 1), ("const", 2)))
        result = json_to_tuples(input_data)
        assert result == expected

    def test_json_to_tuples_with_dict(self):
        """Test converting structure with dictionary."""
        input_data = ["call", "print", [], {"sep": " "}]
        expected = ("call", "print", (), {"sep": " "})
        result = json_to_tuples(input_data)
        assert result == expected

    def test_json_to_tuples_preserves_primitives(self):
        """Test that primitive values are preserved."""
        input_data = ["const", "hello", 42, 3.14, True, None]
        expected = ("const", "hello", 42, 3.14, True, None)
        result = json_to_tuples(input_data)
        assert result == expected

    def test_tuples_to_json_compatible(self):
        """Test converting tuples back to JSON-compatible format."""
        input_data = ("module", (("const", 1), ("const", 2)))
        expected = ["module", [["const", 1], ["const", 2]]]
        result = tuples_to_json_compatible(input_data)
        assert result == expected

    def test_round_trip_conversion(self):
        """Test that conversion is reversible."""
        original = ["module", [["assign", "x", ["const", 42], None]]]

        # Convert to tuples and back
        as_tuples = json_to_tuples(original)
        back_to_lists = tuples_to_json_compatible(as_tuples)

        assert back_to_lists == original


class TestIRParsing:
    """Test IR parsing functions."""

    def test_parse_ir_from_json_string_valid_json(self):
        """Test parsing valid JSON string."""
        json_str = '["module", [["const", 42]]]'
        result = parse_ir_from_json_string(json_str)
        expected = ("module", (("const", 42),))
        assert result == expected

    def test_parse_ir_from_json_string_python_literal(self):
        """Test parsing Python literal with null replacement."""
        python_str = '("module", (("const", null),))'
        result = parse_ir_from_json_string(python_str)
        expected = ("module", (("const", None),))
        assert result == expected

    def test_parse_ir_from_json_string_boolean_replacement(self):
        """Test boolean literal replacement."""
        python_str = '("const", true)'
        result = parse_ir_from_json_string(python_str)
        expected = ("const", True)
        assert result == expected

    def test_parse_ir_from_json_string_empty_input(self):
        """Test parsing empty input raises error."""
        with pytest.raises(IRParseError):
            parse_ir_from_json_string("")

    def test_parse_ir_from_json_string_invalid_input(self):
        """Test parsing invalid input raises error."""
        with pytest.raises(IRParseError):
            parse_ir_from_json_string("invalid json [}")

    def test_parse_ir_from_file_json_format(self):
        """Test parsing IR from JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(["module", [["const", 42]]], f)
            temp_path = f.name

        try:
            result = parse_ir_from_file(temp_path)
            expected = ("module", (("const", 42),))
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_parse_ir_from_file_not_found(self):
        """Test parsing non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_ir_from_file("nonexistent_file.json")

    def test_parse_ir_from_file_directory_error(self):
        """Test parsing directory instead of file raises IRParseError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(IRParseError):
                parse_ir_from_file(temp_dir)


class TestIRValidation:
    """Test IR validation functions."""

    def test_validate_ir_node_format_valid_tuple(self):
        """Test validation of valid IR node tuple."""
        node = ("const", 42)
        assert validate_ir_node_format(node) is True

    def test_validate_ir_node_format_valid_list(self):
        """Test validation of valid IR node list."""
        node = ["const", 42]
        assert validate_ir_node_format(node) is True

    def test_validate_ir_node_format_empty(self):
        """Test validation of empty node."""
        node = ()
        assert validate_ir_node_format(node) is False

    def test_validate_ir_node_format_non_string_opcode(self):
        """Test validation of node with non-string opcode."""
        node = (42, "value")
        assert validate_ir_node_format(node) is False

    def test_validate_ir_node_format_primitive(self):
        """Test validation of primitive value."""
        assert validate_ir_node_format(42) is False
        assert validate_ir_node_format("string") is False

    def test_validate_ir_program_valid(self):
        """Test validation of valid IR program."""
        program = ("module", (("const", 42),))
        assert validate_ir_program(program) is True

    def test_validate_ir_program_not_module(self):
        """Test validation of non-module IR."""
        program = ("const", 42)
        assert validate_ir_program(program) is False

    def test_validate_ir_program_missing_statements(self):
        """Test validation of module without statements."""
        program = ("module",)
        assert validate_ir_program(program) is False

    def test_validate_ir_node_structure_with_opcode(self):
        """Test specific node structure validation."""
        node = ("assign", "x", ("const", 42), None)
        assert validate_ir_node_structure(node, "assign") is True
        assert validate_ir_node_structure(node, "const") is False

    def test_validate_ir_node_structure_with_arg_limits(self):
        """Test node validation with argument count limits."""
        node = ("binary_op", "+", ("const", 1), ("const", 2))

        # Should pass with correct limits
        assert validate_ir_node_structure(node, min_args=3, max_args=3) is True

        # Should fail with incorrect limits
        assert validate_ir_node_structure(node, min_args=4) is False
        assert validate_ir_node_structure(node, max_args=2) is False


class TestIRAnalysis:
    """Test IR analysis utilities."""

    def test_extract_ir_opcodes_simple(self):
        """Test extracting opcodes from simple IR."""
        ir = ("module", (("const", 42), ("assign", "x", ("const", 1), None)))
        opcodes = extract_ir_opcodes(ir)
        expected = {"module", "const", "assign"}
        assert opcodes == expected

    def test_extract_ir_opcodes_nested(self):
        """Test extracting opcodes from nested IR."""
        ir = (
            "if",
            ("binary_op", "<", ("name", "x"), ("const", 0)),
            (("assign", "y", ("const", 1), None),),
            (),
        )
        opcodes = extract_ir_opcodes(ir)
        expected = {"if", "binary_op", "name", "const", "assign"}
        assert opcodes == expected

    def test_count_ir_nodes_simple(self):
        """Test counting IR nodes."""
        ir = ("const", 42)
        assert count_ir_nodes(ir) == 1

    def test_count_ir_nodes_nested(self):
        """Test counting nested IR nodes."""
        ir = ("module", (("const", 42), ("const", 1)))
        # Should count: module, first const, second const = 3 nodes
        assert count_ir_nodes(ir) == 3

    def test_find_ir_nodes_by_opcode(self):
        """Test finding nodes by opcode."""
        ir = ("module", (("const", 42), ("assign", "x", ("const", 1), None)))
        const_nodes = find_ir_nodes_by_opcode(ir, "const")

        assert len(const_nodes) == 2
        assert ("const", 42) in const_nodes
        assert ("const", 1) in const_nodes

    def test_find_ir_nodes_by_opcode_not_found(self):
        """Test finding nodes that don't exist."""
        ir = ("module", (("const", 42),))
        while_nodes = find_ir_nodes_by_opcode(ir, "while")
        assert len(while_nodes) == 0


class TestFileIO:
    """Test file I/O utilities."""

    def test_save_ir_to_file_json_format(self):
        """Test saving IR to JSON file."""
        ir_data = ("module", (("const", 42),))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            save_ir_to_file(ir_data, temp_path, format="json")

            # Read back and verify
            with open(temp_path, "r") as f:
                content = f.read()
                loaded_data = json.loads(content)
                # Should be converted to lists for JSON compatibility
                assert loaded_data == ["module", [["const", 42]]]
        finally:
            os.unlink(temp_path)

    def test_save_ir_to_file_python_format(self):
        """Test saving IR to Python format."""
        ir_data = ("module", (("const", 42),))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            temp_path = f.name

        try:
            save_ir_to_file(ir_data, temp_path, format="python")

            # Read back and verify
            with open(temp_path, "r") as f:
                content = f.read()
                # Should be Python repr format
                assert "('module'," in content
                assert "('const', 42)" in content
        finally:
            os.unlink(temp_path)

    def test_save_ir_to_file_invalid_format(self):
        """Test saving with invalid format raises error."""
        ir_data = ("const", 42)

        with tempfile.NamedTemporaryFile() as f:
            with pytest.raises(IRValidationError):
                save_ir_to_file(ir_data, f.name, format="invalid")

    def test_safe_ir_parse_valid_input(self):
        """Test safe parsing with valid input."""
        content = '["const", 42]'
        result = safe_ir_parse(content)
        assert result == ("const", 42)

    def test_safe_ir_parse_invalid_input(self):
        """Test safe parsing with invalid input returns None."""
        content = "invalid json ["
        result = safe_ir_parse(content)
        assert result is None

    def test_check_file_size_within_limit(self):
        """Test file size checking."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("small content")
            temp_path = f.name

        try:
            assert check_file_size(temp_path) is True
        finally:
            os.unlink(temp_path)

    def test_check_file_size_nonexistent(self):
        """Test file size checking for non-existent file."""
        assert check_file_size("nonexistent_file.txt") is False


class TestDiagnostics:
    """Test diagnostic utilities."""

    def test_get_ir_node_info_valid_node(self):
        """Test getting info about valid IR node."""
        node = ("assign", "x", ("const", 42), None)
        info = get_ir_node_info(node)

        assert info["type"] == "tuple"
        assert info["is_valid_format"] is True
        assert info["length"] == 4
        assert info["opcode"] == "assign"
        assert info["args_count"] == 3

    def test_get_ir_node_info_invalid_node(self):
        """Test getting info about invalid IR node."""
        node = (42, "not an opcode")
        info = get_ir_node_info(node)

        assert info["type"] == "tuple"
        assert info["is_valid_format"] is False
        assert info["opcode"] == "int"  # type name of first element

    def test_get_ir_node_info_primitive(self):
        """Test getting info about primitive value."""
        node = 42
        info = get_ir_node_info(node)

        assert info["type"] == "int"
        assert info["is_valid_format"] is False
        assert info["length"] == 0
        assert info["opcode"] is None


class TestConfiguration:
    """Test configuration and constants."""

    def test_ir_config_constants(self):
        """Test that configuration constants are defined."""
        assert hasattr(IRConfig, "DEFAULT_ENCODING")
        assert hasattr(IRConfig, "CORE_OPCODES")
        assert hasattr(IRConfig, "MAX_FILE_SIZE")
        assert hasattr(IRConfig, "MAX_RECURSION_DEPTH")

    def test_core_opcodes_contains_expected(self):
        """Test that core opcodes contain expected values."""
        expected_opcodes = {
            "module",
            "const",
            "name",
            "assign",
            "call",
            "if",
            "while",
            "for",
        }
        assert expected_opcodes.issubset(IRConfig.CORE_OPCODES)


if __name__ == "__main__":
    pytest.main([__file__])
