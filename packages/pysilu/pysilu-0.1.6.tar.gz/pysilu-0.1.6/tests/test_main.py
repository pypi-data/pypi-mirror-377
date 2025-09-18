"""
Unit tests for the Silu main module.
"""

import sys
import pytest
import subprocess
import os
from unittest.mock import patch
from silu.__main__ import main


def test_main_function(capsys):
    """Test the main function in __main__.py."""
    with patch.object(sys, "argv", ["silu"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "Silu Language Processor" in captured.out


def test_main_as_module_entrypoint():
    """Test running __main__ as a module entrypoint."""
    # This will execute the if __name__ == "__main__": block
    result = subprocess.run(
        [sys.executable, "-m", "silu.__main__"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    assert result.returncode == 1
    assert "Silu Language Processor" in result.stdout


def test_main_import():
    """Test that __main__ can be imported without errors."""
    # Import the module to ensure it can be imported without errors
    import silu.__main__

    assert silu.__main__ is not None
