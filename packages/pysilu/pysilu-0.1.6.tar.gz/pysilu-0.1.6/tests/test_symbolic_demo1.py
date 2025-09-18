import sys
from pathlib import Path

# Add parent directory to path to import Silu modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from silu.symbolic_executor import ExecutionPathState
from silu.symbolic_executor_wrapper import execute_symbolic_from_file_with_executor

"""Test symbolic execution on symbolic_demo1.si.ir.json file."""


def test_symbolic_demo1_paths():
    """Test that symbolic_demo1.si.ir.json has the expected paths and conditions."""
    # Path to the IR file
    ir_file = Path(__file__).parent.parent / "tests" / "symbolic_demo1.si.ir.json"
    assert ir_file.exists(), f"Test file {ir_file} not found"

    # Execute symbolic analysis
    ir_executor_result = execute_symbolic_from_file_with_executor(
        str(ir_file), debug=False
    )

    ir_executor_result = ir_executor_result["function_analyses"]

    paths = next(iter(ir_executor_result.values()))

    # Verify that we have the expected number of paths
    assert len(paths) == 4, f"Expected 4 paths, got {len(paths)}: {paths}"

    # Check that all paths are satisfiable
    for path in paths:
        # assert path.satisfiable, f"Path {path.path_id} should be satisfiable"
        assert path.state == ExecutionPathState.COMPLETED, (
            f"Path {path.path_id} should be completed"
        )

    # Verify that we have all expected return values
    return_values = [str(path.return_value).strip('"') for path in paths]
    expected_returns = ["large_positive", "small_positive", "negative", "zero"]
    for expected in expected_returns:
        assert expected in return_values, f"Missing expected return value: {expected}"

    # Find paths by their return value
    large_positive_path = next(
        p for p in paths if str(p.return_value).strip('"') == "large_positive"
    )
    small_positive_path = next(
        p for p in paths if str(p.return_value).strip('"') == "small_positive"
    )
    negative_path = next(
        p for p in paths if str(p.return_value).strip('"') == "negative"
    )
    zero_path = next(p for p in paths if str(p.return_value).strip('"') == "zero")

    # Check conditions for large_positive path (x > 0 and x > 10)
    assert "x > 0" in [j.expression for j in large_positive_path.conditions]
    assert "x > 10" in [j.expression for j in large_positive_path.conditions]

    # Check conditions for small_positive path (x > 0 and not (x > 10))
    assert "x > 0" in [j.expression for j in small_positive_path.conditions]
    assert any(
        cond.is_true is False and "x > 10" in cond.expression
        for cond in small_positive_path.conditions
    )

    # Check conditions for negative path (not (x > 0) and x < 0)
    assert any(
        cond.is_true is False and "x > 0" in cond.expression
        for cond in negative_path.conditions
    )
    assert "x < 0" in [j.expression for j in negative_path.conditions]

    # Check conditions for zero path (not (x > 0) and not (x < 0))
    assert any(
        cond.is_true is False and "x > 0" in cond.expression
        for cond in zero_path.conditions
    )
    assert any(
        cond.is_true is False and "x < 0" in cond.expression
        for cond in zero_path.conditions
    )

    # Verify test inputs for large_positive (x > 10)
    print(large_positive_path)
    print(
        type(large_positive_path.test_inputs["x"]), large_positive_path.test_inputs["x"]
    )
    assert large_positive_path.test_inputs["x"] > 10

    # Verify test inputs for small_positive (0 < x <= 10)
    assert 0 < small_positive_path.test_inputs["x"] <= 10

    # Verify test inputs for negative (x < 0)
    assert negative_path.test_inputs["x"] < 0

    # Verify test inputs for zero (x == 0)
    assert zero_path.test_inputs["x"] == 0


if __name__ == "__main__":
    # pytest.main(["-xvs", __file__])
    test_symbolic_demo1_paths()
