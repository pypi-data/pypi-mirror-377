"""
Unit tests for the Silu CLI module.
"""

import sys
import ast
import pytest
from silu.cli import main
from unittest.mock import patch, mock_open


def test_main_with_no_arguments(capsys):
    """Test main function with no arguments shows help."""
    with patch.object(sys, "argv", ["silu"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Silu Language Processor" in captured.out
    assert "interpret" in captured.out
    assert "ir" in captured.out


def test_main_with_invalid_mode(capsys):
    """Test main function with invalid mode shows help."""
    with patch.object(sys, "argv", ["silu", "invalid_mode"]):
        with patch("silu.cli.Path.exists", return_value=False):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "File 'invalid_mode' not found" in captured.err


@patch("builtins.open", new_callable=mock_open, read_data="x = 42\nprint(x)")
@patch("silu.cli.ast.parse")
def test_legacy_usage_with_valid_file(mock_parse, mock_file):
    """Test legacy usage (silu file.si) with a valid file."""
    # Create a mock AST
    mock_tree = ast.parse("x = 42\nprint(x)")
    mock_parse.return_value = mock_tree

    with patch.object(sys, "argv", ["silu", "test.si"]):
        with patch("silu.cli.SiluInterpreter") as mock_interpreter:
            # This should not raise an exception for legacy usage
            main()

            # Verify the file was opened and interpreter was created
            mock_file.assert_called_once_with("test.si", "r", encoding="utf-8")
            # Legacy usage should call parse at least once
            assert mock_parse.call_count >= 1
            mock_interpreter.assert_called_once()


@patch("silu.cli.read_source_file")
def test_interpret_mode_with_valid_file(mock_read_file, capsys):
    """Test interpret mode with a valid file."""
    mock_read_file.return_value = "x = 42\nprint(x)"

    with patch.object(sys, "argv", ["silu", "interpret", "test.si"]):
        with patch("silu.cli.Path.exists", return_value=True):
            with patch("silu.cli.run_interpreter") as mock_run:
                main()
                mock_run.assert_called_once_with("x = 42\nprint(x)")


@patch("silu.cli.read_source_file")
def test_ir_mode_with_valid_file(mock_read_file, capsys):
    """Test IR mode with a valid file."""
    mock_read_file.return_value = "x = 42\nprint(x)"

    with patch.object(sys, "argv", ["silu", "ir", "test.si"]):
        with patch("silu.cli.Path.exists", return_value=True):
            with patch("silu.cli.generate_ir") as mock_generate:
                main()
                mock_generate.assert_called_once_with(
                    "x = 42\nprint(x)", "pretty", record_types=True
                )


def test_interpret_mode_with_source_string(capsys):
    """Test interpret mode with source string."""
    with patch.object(sys, "argv", ["silu", "interpret", "--source", "x = 5"]):
        with patch("silu.cli.run_interpreter") as mock_run:
            main()
            mock_run.assert_called_once_with("x = 5")


def test_ir_mode_with_source_string_and_format(capsys):
    """Test IR mode with source string and JSON format."""
    with patch.object(
        sys, "argv", ["silu", "ir", "--source", "x = 5", "--format", "json"]
    ):
        with patch("silu.cli.generate_ir") as mock_generate:
            main()
            mock_generate.assert_called_once_with("x = 5", "json", record_types=True)


def test_main_with_nonexistent_file(capsys):
    """Test main function with a nonexistent file."""
    with patch.object(sys, "argv", ["silu", "interpret", "nonexistent.si"]):
        with patch("silu.cli.Path.exists", return_value=False):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "does not exist" in captured.err


def test_main_with_syntax_error(capsys):
    """Test main function with a file containing syntax errors."""
    with patch.object(sys, "argv", ["silu", "interpret", "--source", "x = = 42"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Syntax Error" in captured.err


def test_main_with_missing_file_and_source(capsys):
    """Test main function when neither file nor source is provided."""
    with patch.object(sys, "argv", ["silu", "interpret"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Either a source file or --source must be provided" in captured.err


def test_main_with_both_file_and_source(capsys):
    """Test main function when both file and source are provided."""
    with patch.object(
        sys, "argv", ["silu", "interpret", "test.si", "--source", "x = 5"]
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Cannot specify both file and --source" in captured.err


def test_ir_mode_with_output_file():
    """Test IR mode with output file."""
    with patch.object(
        sys, "argv", ["silu", "ir", "--source", "x = 5", "--output", "test.ir"]
    ):
        with patch("silu.cli.ast.parse") as mock_parse:
            with patch("silu.cli.SiluIRGenerator") as mock_ir_gen:
                with patch("silu.cli.save_ir_to_file") as mock_save:
                    mock_tree = ast.parse("x = 5")
                    mock_parse.return_value = mock_tree
                    mock_ir_gen.return_value.visit.return_value = ("module", [])

                    main()

                    mock_save.assert_called_once()


def test_cli_as_module():
    """Test that the CLI can be called as a module."""
    # This test just ensures the module structure is correct
    import silu.cli

    assert hasattr(silu.cli, "main")
    assert callable(silu.cli.main)


def test_cli_integration():
    """Integration test to verify the CLI works end-to-end."""
    # Test that we can import and the main function exists
    from silu.cli import main

    assert callable(main)

    # Test help output
    with patch.object(sys, "argv", ["silu", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Help should exit with code 0
        assert exc_info.value.code == 0


def test_debug_mode():
    """Test debug mode functionality."""
    with patch.object(
        sys, "argv", ["silu", "interpret", "--source", "x = 5", "--debug"]
    ):
        with patch("silu.cli.run_interpreter") as mock_run:
            main()
            mock_run.assert_called_once_with("x = 5")


def test_no_types_flag():
    """Test --no-types flag for IR generation."""
    with patch.object(sys, "argv", ["silu", "ir", "--source", "x = 5", "--no-types"]):
        with patch("silu.cli.generate_ir") as mock_generate:
            main()
            mock_generate.assert_called_once_with("x = 5", "pretty", record_types=False)
