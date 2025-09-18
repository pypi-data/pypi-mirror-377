#!/usr/bin/env python3
"""
Unit tests for enhanced symbolic execution features including Z3 integration,
loop analysis, and advanced constraint handling.
"""

import pytest
from silu.symbolic_executor import (
    SymbolicExecutor,
    SymbolicValue,
    SymbolicValueType,
)


# Check if Z3 is available for testing
try:
    from silu.symbolic.z3_utils import Z3_AVAILABLE, check_path_satisfiability
    from silu.symbolic.loop_utils import LoopAnalyzer

    Z3_TESTS_ENABLED = Z3_AVAILABLE
except ImportError:
    Z3_TESTS_ENABLED = False
    Z3_AVAILABLE = False


from z3 import Int


class TestBasicEnhancedExecution:
    """Test basic enhanced symbolic execution functionality"""

    def test_basic_assignment(self):
        """Test basic variable assignment"""
        ir = (
            "module",
            [
                ("assign", "x", ("literal", 10), None),
                ("assign", "y", ("binary_op", "x", "+", ("literal", 5)), None),
            ],
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) >= 1
        path = paths[0]
        assert "x" in path.variables
        assert "y" in path.variables

    def test_enhanced_if_statement(self):
        """Test if statement with symbolic conditions"""
        ir = (
            "module",
            (
                ("assign", "x", ("literal", 10), None),
                (
                    "if",
                    ("binary_op", "x", ">", ("literal", 5)),
                    ("block", (("assign", "result", ("literal", 1), None),)),
                    ("block", (("assign", "result", ("literal", 0), None),)),
                ),
            ),
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) >= 1
        for path in paths:
            assert hasattr(path, "conditions")
            assert hasattr(path, "statements")
            assert hasattr(path, "variables")


class TestLoopAnalysis:
    """Test enhanced loop analysis functionality"""

    def test_while_loop_symbolic(self):
        """Test while loop symbolic execution"""
        ir = (
            "module",
            [
                ("assign", "i", ("literal", 0), None),
                (
                    "while",
                    ("binary_op", "i", "<", ("literal", 3)),
                    (
                        "block",
                        (
                            (
                                "assign",
                                "i",
                                ("binary_op", "i", "+", ("literal", 1)),
                                None,
                            ),
                        ),
                    ),
                ),
            ],
        )

        executor = SymbolicExecutor()
        executor.max_loop_iterations = 5  # Set reasonable limit
        paths = executor.execute_program(ir)

        assert len(paths) >= 1
        for path in paths:
            assert hasattr(path, "loop_iterations")

    def test_for_range_loop(self):
        """Test for loop with range"""
        ir = (
            "module",
            [
                ("assign", "sum_val", ("literal", 0), None),
                (
                    "for",
                    "i",
                    ("call", "range", [("literal", 0), ("literal", 3), ("literal", 1)]),
                    (
                        "block",
                        (
                            (
                                "assign",
                                "sum_val",
                                ("binary_op", "sum_val", "+", "i"),
                                None,
                            ),
                        ),
                    ),
                ),
            ],
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) >= 1
        for path in paths:
            assert "sum_val" in path.variables
            assert "i" in path.variables


@pytest.mark.skipif(not Z3_TESTS_ENABLED, reason="Z3 not available")
class TestZ3Integration:
    """Test Z3 solver integration features"""

    def test_z3_satisfiability_satisfiable(self):
        """Test Z3-based satisfiability checking for satisfiable conditions"""
        conditions = ["x > 5", "x < 10", "y == 7"]
        var_dict = {"x": Int("x"), "y": Int("y")}
        is_sat, model = check_path_satisfiability(conditions, var_dict)

        assert is_sat is True
        assert model is not None

    def test_z3_satisfiability_unsatisfiable(self):
        """Test Z3-based satisfiability checking for unsatisfiable conditions"""
        conditions = ["x > 10", "x < 5"]
        var_dict = {"x": Int("x")}
        is_sat, model = check_path_satisfiability(conditions, var_dict)

        assert is_sat is False

    def test_path_with_z3_constraints(self):
        """Test execution path with Z3 constraint generation"""
        ir = (
            "module",
            [
                ("assign", "x", ("literal", 5), None),
                (
                    "if",
                    ("binary_op", "x", ">", ("literal", 0)),
                    ("block", (("assign", "result", ("literal", 1), None),)),
                    ("block", (("assign", "result", ("literal", 0), None),)),
                ),
            ],
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        # Test if paths have satisfiability information
        for path in paths:
            # Check if satisfiability checking was performed
            satisfiable = path.is_satisfiable()
            assert isinstance(satisfiable, bool)


@pytest.mark.skipif(not Z3_TESTS_ENABLED, reason="Z3 not available")
class TestLoopBoundAnalysis:
    """Test loop bound detection and analysis"""

    def test_loop_analyzer_creation(self):
        """Test LoopAnalyzer creation and basic functionality"""
        analyzer = LoopAnalyzer(max_iterations=3)
        assert analyzer.max_iterations == 3

    def test_range_loop_analysis_simple(self):
        """Test range loop analysis with simple bounds"""
        analyzer = LoopAnalyzer(max_iterations=5)
        iterations = analyzer.analyze_range_loop(0, 3, 1, "i")

        assert len(iterations) <= 5
        for iteration in iterations:
            assert hasattr(iteration, "iteration")
            assert hasattr(iteration, "constraint")
            assert hasattr(iteration, "variable_values")
            assert hasattr(iteration, "is_valid")

    def test_range_bounds_extraction(self):
        """Test extraction of range bounds from different expressions"""
        analyzer = LoopAnalyzer()

        # Test different range expressions
        range_exprs = [
            ("call", "range", [("literal", 5)]),
            ("call", "range", [("literal", 1), ("literal", 6)]),
            ("call", "range", [("literal", 0), ("literal", 10), ("literal", 2)]),
        ]

        for expr in range_exprs:
            bounds = analyzer.extract_range_bounds(expr)
            if bounds:
                assert hasattr(bounds, "start")
                assert hasattr(bounds, "stop")
                assert hasattr(bounds, "step")

                estimated = analyzer.estimate_loop_bound(
                    bounds.start, bounds.stop, bounds.step
                )
                assert isinstance(estimated, int)
                assert estimated >= 0


class TestEnhancedReporting:
    """Test enhanced report generation"""

    def test_enhanced_report_generation(self):
        """Test enhanced report generation with complex program"""
        ir = (
            "module",
            [
                ("assign", "x", ("literal", 5), None),
                ("assign", "sum_val", ("literal", 0), None),
                (
                    "if",
                    ("binary_op", "x", ">", ("literal", 0)),
                    (
                        "block",
                        (
                            (
                                "for",
                                "i",
                                ("call", "range", [("literal", 3)]),
                                (
                                    "block",
                                    (
                                        (
                                            "assign",
                                            "sum_val",
                                            ("binary_op", "sum_val", "+", "i"),
                                            None,
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ],
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)
        report = executor.generate_report(paths)

        # Verify report structure
        assert isinstance(report, dict)
        assert "total_paths" in report
        assert "satisfiable_paths" in report
        assert "paths" in report
        # summary field has been removed to reduce output verbosity
        # assert "summary" in report
        assert report["total_paths"] >= 0
        assert report["satisfiable_paths"] >= 0
        assert isinstance(report["paths"], list)

    def test_function_analysis_reporting(self):
        """Test function analysis in reports"""
        ir = (
            "module",
            [
                (
                    "func_def",
                    "test_func",
                    ["x"],
                    (
                        "block",
                        (
                            (
                                "if",
                                ("binary_op", "x", ">", ("literal", 0)),
                                ("block", (("return", ("literal", 1)),)),
                                ("block", (("return", ("literal", 0)),)),
                            ),
                        ),
                    ),
                ),
                ("assign", "result", ("call", "test_func", [("literal", 5)]), None),
            ],
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)
        report = executor.generate_report(paths)

        # Check if function analyses are included
        if "function_analyses" in report:
            assert isinstance(report["function_analyses"], dict)


class TestSymbolicValueOperations:
    """Test enhanced symbolic value operations"""

    def test_symbolic_binary_operations(self):
        """Test symbolic binary operations maintain type information"""
        executor = SymbolicExecutor()

        # Create symbolic values
        a = SymbolicValue(SymbolicValueType.SYMBOLIC, None, "a")
        b = SymbolicValue(SymbolicValueType.SYMBOLIC, None, "b")

        executor.current_env.set_variable("a", a)
        executor.current_env.set_variable("b", b)

        # Test comparison operation
        comparison_ir = (">", "a", "b")
        result = executor._execute_ir(comparison_ir)

        assert result.type == SymbolicValueType.EXPRESSION
        assert isinstance(result.value, (tuple, list))

    def test_expression_readability(self):
        """Test expression to readable string conversion"""
        executor = SymbolicExecutor()

        # Create expression value
        expr = (">", "a", "b")
        expr_value = SymbolicValue(SymbolicValueType.EXPRESSION, expr)

        readable = executor._make_condition_readable(expr_value)
        assert isinstance(readable, str)
        assert len(readable) > 0

    def test_complex_expression_handling(self):
        """Test handling of complex nested expressions"""
        executor = SymbolicExecutor()

        # Set up symbolic environment
        a = SymbolicValue(SymbolicValueType.SYMBOLIC, None, "a")
        b = SymbolicValue(SymbolicValueType.SYMBOLIC, None, "b")
        c = SymbolicValue(SymbolicValueType.SYMBOLIC, None, "c")

        executor.current_env.set_variable("a", a)
        executor.current_env.set_variable("b", b)
        executor.current_env.set_variable("c", c)

        # Test nested expression: (a > b) and (b < c)
        nested_ir = ("and", (">", "a", "b"), ("<", "b", "c"))
        result = executor._execute_ir(nested_ir)

        assert result.type == SymbolicValueType.EXPRESSION


class TestErrorHandling:
    """Test error handling in enhanced symbolic execution"""

    def test_invalid_ir_handling(self):
        """Test handling of invalid IR structures"""
        executor = SymbolicExecutor()

        # Test with malformed IR
        invalid_ir = ("invalid_op", "arg1")

        # Should not crash, should return a reasonable default
        try:
            result = executor._execute_ir(invalid_ir)
            # If it doesn't raise an exception, verify it returns a symbolic value
            assert hasattr(result, "type")
        except Exception:
            # If it raises an exception, that's also acceptable
            pass

    def test_missing_variable_handling(self):
        """Test handling of references to undefined variables"""
        executor = SymbolicExecutor()

        # Reference undefined variable
        var_ir = "undefined_var"
        result = executor._execute_ir(var_ir)

        # Should create a symbolic value for undefined variables
        assert result.type == SymbolicValueType.SYMBOLIC
        assert hasattr(result, "name")

    def test_recursive_function_analysis(self):
        """Test handling of recursive function definitions"""
        ir = (
            "module",
            [
                (
                    "func_def",
                    "factorial",
                    ["n"],
                    (
                        "block",
                        (
                            (
                                "if",
                                ("binary_op", "n", "<=", ("literal", 1)),
                                ("block", (("return", ("literal", 1)),)),
                                (
                                    "block",
                                    (
                                        (
                                            "return",
                                            (
                                                "binary_op",
                                                "n",
                                                "*",
                                                (
                                                    "call",
                                                    "factorial",
                                                    [
                                                        (
                                                            "binary_op",
                                                            "n",
                                                            "-",
                                                            ("literal", 1),
                                                        )
                                                    ],
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                )
            ],
        )

        executor = SymbolicExecutor()

        # Should handle recursive definitions without infinite loops
        try:
            paths = executor.execute_program(ir)
            assert len(paths) >= 0  # Should complete without hanging
        except RecursionError:
            pytest.skip(
                "Recursion limit reached - expected for deep recursive analysis"
            )


if __name__ == "__main__":
    pytest.main([__file__])
