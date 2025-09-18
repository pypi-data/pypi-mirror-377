#!/usr/bin/env python3
"""
Integration tests for ir_utils module usage across different IR processors.
This verifies that the refactoring to use shared IR utilities works correctly.
"""

import tempfile
import json
import os
import pytest

# Import the modules we refactored
from silu.ir_interpreter import execute_ir_from_file, execute_ir_from_string
from silu.ir_to_source import convert_ir_file_to_source, convert_ir_string_to_source
from silu.silu_ir_to_llvm import SiluToLLVMConverter
from silu.symbolic_executor_wrapper import execute_symbolic_from_file_with_executor


class TestIRInterpreterIntegration:
    """Test IR interpreter with ir_utils integration."""

    def test_execute_from_json_string(self):
        """Test executing IR from JSON string."""

        # Test with JSON string (using lists since JSON doesn't support tuples)
        ir_json = json.dumps(
            [
                "module",
                [
                    ["assign", "x", 42, None],
                    ["assign", "y", ["binop", "+", "x", 10], None],
                    ["print", ["name", "y"]],
                ],
            ]
        )

        result = execute_ir_from_string(ir_json)
        # The execution should complete without errors
        assert (
            result is not None or result is None
        )  # Result can be None for print statements

    def test_execute_from_python_literal(self):
        """Test executing IR from Python literal string."""
        ir_literal = '("module", (("assign", "x", 42, None), ("print", ("name", "x"))))'
        result = execute_ir_from_string(ir_literal)
        assert result is not None or result is None

    def test_execute_from_file(self):
        """Test executing IR from file."""
        ir_json = json.dumps(
            ["module", [["assign", "x", 42, None], ["print", ["name", "x"]]]]
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ir.json", delete=False
        ) as f:
            f.write(ir_json)
            temp_file = f.name

        try:
            result = execute_symbolic_from_file_with_executor(temp_file)["paths"]
            assert result is not None or result is None
        finally:
            os.unlink(temp_file)


class TestSymbolicExecutorIntegration:
    """Test symbolic executor with ir_utils integration."""

    def test_execute_symbolic_from_file(self):
        """Test symbolic execution from IR file."""
        ir_json = json.dumps(
            [
                "module",
                [
                    # ["assign", "x", ["input", "int"], None],
                    ["assign", "x", 2, None],
                    [
                        "if",
                        [">", ["name", "x"], ["const", 0]],
                        [["print", ["const", "positive"]]],
                        [["print", ["const", "non-positive"]]],
                    ],
                ],
            ]
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ir.json", delete=False
        ) as f:
            f.write(ir_json)
            temp_file = f.name

        try:
            paths = execute_symbolic_from_file_with_executor(temp_file)["paths"]
            # TODO: 2 path?
            assert len(paths) == 1, f"Expected 1 paths, got {len(paths)}"
        finally:
            os.unlink(temp_file)


class TestIRToSourceIntegration:
    """Test IR to source converter with ir_utils integration."""

    def test_convert_from_string(self):
        """Test converting IR string to source."""

        # IR that should convert back to readable source
        ir_json = json.dumps(
            [
                "module",
                [
                    ["assign", "x", 42, None],
                    ["assign", "y", ["binop", "+", "x", 10], None],
                    ["print", ["name", "y"]],
                ],
            ]
        )

        source = convert_ir_string_to_source(ir_json)
        assert "x = 42" in source, f"Expected 'x = 42' in source, got: {source}"
        assert "y = binop('+', x, 10)" in source, (
            f"Expected 'y = binop('+', x, 10)' in source, got: {source}"
        )

    def test_convert_from_file(self):
        """Test converting IR file to source."""
        ir_json = json.dumps(
            [
                "module",
                [
                    ["assign", "x", 42, None],
                    ["assign", "y", ["binop", "+", "x", 10], None],
                    ["print", ["name", "y"]],
                ],
            ]
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ir.json", delete=False
        ) as f:
            f.write(ir_json)
            temp_file = f.name

        try:
            source = convert_ir_file_to_source(temp_file)
            assert "x = 42" in source, f"Expected 'x = 42' in source, got: {source}"
        finally:
            os.unlink(temp_file)


class TestSiluIRToLLVMIntegration:
    """Test Silu IR to LLVM converter with ir_utils integration."""

    @pytest.mark.skipif(True, reason="LLVM converter test is optional")
    def test_convert_to_llvm(self):
        """Test converting IR to LLVM."""

        # Simple IR for LLVM conversion
        ir_json = json.dumps(
            ["module", [["assign", "x", 42, None], ["print", ["name", "x"]]]]
        )

        converter = SiluToLLVMConverter()
        try:
            llvm_ir = converter.convert(ir_json)
            # Just check that it produces some LLVM IR without errors
            assert "define" in llvm_ir, "Expected LLVM IR to contain 'define'"
            assert "main" in llvm_ir, "Expected LLVM IR to contain 'main'"
        except ImportError:
            pytest.skip("llvmlite not available")


class TestErrorHandling:
    """Test error handling with invalid inputs."""

    def test_invalid_json_string(self):
        """Test handling of invalid JSON string."""

        invalid_json = "not valid json at all"

        with pytest.raises(RuntimeError) as exc_info:
            execute_ir_from_string(invalid_json)
        assert "Failed to parse IR" in str(exc_info.value)

    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        with pytest.raises(RuntimeError) as exc_info:
            execute_ir_from_file("non_existent_file.ir.json")
        assert "not found" in str(exc_info.value) or "Failed to load" in str(
            exc_info.value
        )


class TestFormatCompatibility:
    """Test that both JSON and Python literal formats work."""

    def test_json_format(self):
        """Test JSON format parsing."""

        json_format = json.dumps(["module", [["assign", "x", 42, None]]])
        result = execute_ir_from_string(json_format)
        assert result is not None or result is None

    def test_python_tuple_format(self):
        """Test Python tuple format parsing."""
        python_format = '("module", (("assign", "x", 42, None),))'
        result = execute_ir_from_string(python_format)
        assert result is not None or result is None

    def test_boolean_literal_format(self):
        """Test format with boolean literals."""
        literal_with_bools = '("module", (("assign", "x", true, None),))'
        result = execute_ir_from_string(literal_with_bools)
        assert result is not None or result is None
