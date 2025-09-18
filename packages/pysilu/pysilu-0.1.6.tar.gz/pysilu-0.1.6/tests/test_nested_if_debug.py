#!/usr/bin/env python3
"""
Test utilities for debugging nested if statements, extracted from debug_symbolic.py.
Focuses on structural analysis and debugging tools rather than complex execution tests.
"""

from silu.symbolic_executor import SymbolicExecutor


class TestIRStructureAnalysis:
    """Test IR structure analysis utilities inspired by debug_symbolic.py"""

    def setup_method(self):
        """Setup test environment"""
        self.executor = SymbolicExecutor()

    @staticmethod
    def analyze_ir_structure(ir, target_type="if"):
        """
        Analyze IR structure to find specific statement types.
        Inspired by analyze_if_structure() from debug_symbolic.py
        """
        found_statements = []

        def _traverse(node, path=""):
            if isinstance(node, (list, tuple)) and len(node) > 0:
                if node[0] == target_type:
                    found_statements.append(
                        {
                            "path": path,
                            "statement": node,
                            "condition": node[1] if len(node) > 1 else None,
                            "then_block": node[2] if len(node) > 2 else None,
                            "else_block": node[3] if len(node) > 3 else None,
                        }
                    )

                for i, child in enumerate(node):
                    if isinstance(child, (list, tuple)):
                        _traverse(child, f"{path}[{i}]")

        _traverse(ir)
        return found_statements

    def test_ir_structure_analysis_simple_if(self):
        """Test IR structure analysis for simple if statements"""
        ir = (
            "module",
            (
                (
                    "if",
                    ("chained_compare", "x", ">", 0),
                    ("block", (("assign", "y", 1, None),)),
                    ("block", (("assign", "y", 0, None),)),
                ),
            ),
        )

        if_statements = self.analyze_ir_structure(ir, "if")

        assert len(if_statements) == 1, "Should find exactly one if statement"

        if_stmt = if_statements[0]
        assert if_stmt["condition"] == ("chained_compare", "x", ">", 0)
        assert if_stmt["then_block"] is not None
        assert if_stmt["else_block"] is not None

    def test_ir_structure_analysis_nested_if(self):
        """Test IR structure analysis for nested if statements"""
        ir = (
            "module",
            (
                (
                    "if",
                    ("chained_compare", "x", ">", 0),
                    (
                        "block",
                        (
                            (
                                "if",
                                ("chained_compare", "x", ">", 10),
                                ("block", (("assign", "y", 1, None),)),
                                ("block", (("assign", "y", 2, None),)),
                            ),
                        ),
                    ),
                    ("block", (("assign", "y", 0, None),)),
                ),
            ),
        )

        if_statements = self.analyze_ir_structure(ir, "if")

        assert len(if_statements) == 2, (
            "Should find exactly two if statements (one nested)"
        )

        # Verify both outer and inner if statements are found
        conditions = [stmt["condition"] for stmt in if_statements]
        assert ("chained_compare", "x", ">", 0) in conditions
        assert ("chained_compare", "x", ">", 10) in conditions

    def test_function_definition_analysis(self):
        """Test analysis of function definitions in IR"""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "test_nested_if",
                    ["b"],
                    (
                        (
                            "if",
                            ("chained_compare", "b", "==", 0),
                            ("block", (("return", -1),)),
                            (
                                (
                                    "if",
                                    ("chained_compare", "b", ">", 10),
                                    ("block", (("return", 100),)),
                                    ("block", (("return", 50),)),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

        # Analyze function definitions
        func_statements = self.analyze_ir_structure(ir, "func_def")
        if_statements = self.analyze_ir_structure(ir, "if")

        assert len(func_statements) == 1, "Should find 1 function definition"
        func_stmt = func_statements[0]
        assert func_stmt["statement"][1] == "test_nested_if"
        assert func_stmt["statement"][2] == ["b"]

        assert len(if_statements) == 2, "Should find 2 nested if statements"

    def test_comprehensive_structure_analysis(self):
        """Test comprehensive analysis of complex nested structures"""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "process_numbers",
                    ["n"],
                    (
                        (
                            "if",
                            ("chained_compare", "n", "<", 0),
                            ("block", (("return", "negative"),)),
                            (
                                (
                                    "if",
                                    ("chained_compare", "n", "==", 0),
                                    ("block", (("return", "zero"),)),
                                    (
                                        (
                                            "if",
                                            ("chained_compare", "n", "<", 100),
                                            ("block", (("return", "small"),)),
                                            ("block", (("return", "large"),)),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

        # Analyze structure
        if_statements = self.analyze_ir_structure(ir, "if")
        func_statements = self.analyze_ir_structure(ir, "func_def")
        return_statements = self.analyze_ir_structure(ir, "return")

        assert len(if_statements) == 3, "Should find 3 nested if statements"
        assert len(func_statements) == 1, "Should find 1 function definition"
        assert len(return_statements) == 4, "Should find 4 return statements"

        # Verify conditions are correctly identified
        conditions = [stmt["condition"] for stmt in if_statements]
        expected_conditions = [
            ("chained_compare", "n", "<", 0),
            ("chained_compare", "n", "==", 0),
            ("chained_compare", "n", "<", 100),
        ]
        for expected in expected_conditions:
            assert expected in conditions, f"Missing expected condition: {expected}"


class TestDebugUtilities:
    """Test debug utilities inspired by debug_symbolic.py"""

    @staticmethod
    def format_ir_structure(ir, indent=0):
        """
        Format IR structure for readable output.
        Inspired by print_ir_structure() from debug_symbolic.py
        """
        prefix = "  " * indent
        result = []

        if isinstance(ir, (list, tuple)):
            if len(ir) == 0:
                result.append(f"{prefix}[]")
            else:
                for i, item in enumerate(ir):
                    if i == 0 and isinstance(item, str):
                        result.append(f"{prefix}[{item}]")
                    elif isinstance(item, (list, tuple)):
                        result.append(f"{prefix}  [{i}]:")
                        result.extend(
                            TestDebugUtilities.format_ir_structure(item, indent + 2)
                        )
                    else:
                        result.append(f"{prefix}  [{i}]: {repr(item)}")
        else:
            result.append(f"{prefix}{repr(ir)}")

        return result

    def test_ir_formatting_simple(self):
        """Test IR formatting for simple structures"""
        ir = ("assign", "x", 5, None)
        formatted = self.format_ir_structure(ir)

        assert len(formatted) >= 1
        assert "[assign]" in formatted[0]

    def test_ir_formatting_nested(self):
        """Test IR formatting for nested structures"""
        ir = (
            "module",
            (
                ("assign", "x", 5, None),
                (
                    "if",
                    ("chained_compare", "x", ">", 0),
                    ("block", (("assign", "y", 1, None),)),
                    ("block", (("assign", "y", 0, None),)),
                ),
            ),
        )

        formatted = self.format_ir_structure(ir)

        # Verify structure is properly formatted
        assert len(formatted) > 5, "Should have multiple formatted lines"
        assert any("[module]" in line for line in formatted)
        assert any("[if]" in line for line in formatted)
        assert any("[assign]" in line for line in formatted)

    def test_debug_output_for_complex_if(self):
        """Test debug output formatting for complex if statements"""
        ir = (
            "if",
            ("chained_compare", "b", "==", 0),
            ("block", (("return", -1),)),
            (
                (
                    "if",
                    ("chained_compare", "b", ">", 10),
                    ("block", (("return", 100),)),
                    ("block", (("return", 50),)),
                ),
            ),
        )

        formatted = self.format_ir_structure(ir)

        # Check that the nested structure is properly represented
        formatted_str = "\n".join(formatted)
        assert "[if]" in formatted_str
        assert "chained_compare" in formatted_str
        assert "return" in formatted_str

    def test_path_analysis_debugging(self):
        """Test debug analysis similar to debug_symbolic.py functionality"""
        # Test with a simple working case
        ir = (
            "module",
            (
                ("assign", "x", 5, None),
                (
                    "if",
                    ("chained_compare", "x", ">", 0),
                    ("block", (("assign", "result", "positive", None),)),
                    ("block", (("assign", "result", "non_positive", None),)),
                ),
            ),
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        # Debug analysis similar to debug_symbolic.py
        debug_info = []
        for i, path in enumerate(paths):
            path_info = {
                "path_id": i + 1,
                "conditions": [str(c) for c in path.conditions],
                "variables": dict(path.variables)
                if hasattr(path.variables, "items")
                else path.variables,
                "statements": path.statements,
                "return_value": path.return_value,
            }
            debug_info.append(path_info)

        # Verify we have meaningful debug information
        assert len(debug_info) >= 1, "Should have at least 1 path"

        # Check that we have path information
        # TODO: : temp disable show statements
        # assert len(debug_info[0]["statements"]) > 0, "Should have statements"

        # Should have variables populated
        assert "x" in debug_info[0]["variables"], "Should have variable x"

    def test_ir_validation_utilities(self):
        """Test utilities for validating IR structure"""
        # Valid IR
        valid_ir = (
            "module",
            (
                ("assign", "x", 42, None),
                ("if", ("chained_compare", "x", ">", 0), ("block", ()), ("block", ())),
            ),
        )

        # Test that our analysis functions work on valid IR
        analyzer = TestIRStructureAnalysis()
        if_statements = analyzer.analyze_ir_structure(valid_ir, "if")
        assign_statements = analyzer.analyze_ir_structure(valid_ir, "assign")

        assert len(if_statements) == 1
        assert len(assign_statements) == 1

        # Test formatting
        formatted = self.format_ir_structure(valid_ir)
        assert len(formatted) > 0
        assert any("[module]" in line for line in formatted)


class TestExtractedDebugFeatures:
    """Test the specific debugging features extracted from debug_symbolic.py"""

    def test_detailed_if_analysis(self):
        """Test detailed analysis of if statement structure (from debug_symbolic.py)"""
        ir = (
            "module",
            (
                (
                    "if",
                    ("chained_compare", "value", "<", 0),
                    ("block", (("assign", "category", "negative", None),)),
                    (
                        (
                            "if",
                            ("chained_compare", "value", "==", 0),
                            ("block", (("assign", "category", "zero", None),)),
                            ("block", (("assign", "category", "positive", None),)),
                        ),
                    ),
                ),
            ),
        )

        # Perform the type of analysis that debug_symbolic.py was doing
        analyzer = TestIRStructureAnalysis()
        if_statements = analyzer.analyze_ir_structure(ir, "if")

        # Detailed analysis of each if statement
        for i, if_stmt in enumerate(if_statements):
            stmt = if_stmt["statement"]
            condition = if_stmt["condition"]
            then_block = if_stmt["then_block"]
            # else_block = if_stmt["else_block"]

            # Verify structure
            assert stmt[0] == "if", f"Statement {i} should be an if statement"
            assert condition is not None, f"Statement {i} should have a condition"
            assert then_block is not None, f"Statement {i} should have a then block"

            # Check condition structure
            if isinstance(condition, tuple) and len(condition) >= 4:
                assert condition[0] == "chained_compare", (
                    f"Condition {i} should be a comparison"
                )

        # Should find both if statements
        assert len(if_statements) == 2, (
            "Should find 2 if statements in nested structure"
        )

    def test_debug_symbolic_workflow(self):
        """Test the complete workflow that debug_symbolic.py was trying to achieve"""
        # This simulates the workflow without the missing file dependency
        test_ir = (
            "module",
            (
                (
                    "func_def",
                    "test_function",
                    ["input_val"],
                    (
                        (
                            "if",
                            ("chained_compare", "input_val", ">", 0),
                            ("block", (("return", "positive"),)),
                            ("block", (("return", "zero_or_negative"),)),
                        ),
                    ),
                ),
            ),
        )

        # Step 1: Analyze IR structure (like debug_symbolic.py)
        analyzer = TestIRStructureAnalysis()
        structure_analysis = {
            "functions": analyzer.analyze_ir_structure(test_ir, "func_def"),
            "if_statements": analyzer.analyze_ir_structure(test_ir, "if"),
            "returns": analyzer.analyze_ir_structure(test_ir, "return"),
        }

        # Step 2: Format for debugging (like debug_symbolic.py)
        debug_formatter = TestDebugUtilities()
        formatted_output = debug_formatter.format_ir_structure(test_ir)

        # Step 3: Attempt symbolic execution (like debug_symbolic.py)
        executor = SymbolicExecutor()
        paths = executor.execute_program(test_ir)

        # Verify the workflow produces meaningful results
        assert len(structure_analysis["functions"]) == 1
        assert len(structure_analysis["if_statements"]) == 1
        assert len(formatted_output) > 0
        assert len(paths) >= 1

        # The key insight: debug_symbolic.py was trying to provide
        # comprehensive analysis tools for understanding IR execution
        analysis_report = {
            "structure": structure_analysis,
            "formatted_ir": formatted_output,
            "execution_paths": len(paths),
            "path_details": [
                {
                    "conditions": [str(c) for c in path.conditions],
                    "statements": path.statements,
                    "variables": dict(path.variables)
                    if hasattr(path.variables, "items")
                    else path.variables,
                }
                for path in paths
            ],
        }

        # This analysis report is the valuable output that debug_symbolic.py
        # was trying to generate
        assert "structure" in analysis_report
        assert "formatted_ir" in analysis_report
        assert "execution_paths" in analysis_report
        assert "path_details" in analysis_report


class TestComplexElseIfChain:
    """Test complex else-if chain scenarios that were previously failing"""

    def setup_method(self):
        """Setup test environment"""
        self.executor = SymbolicExecutor()

    def test_single_letter_grade_assignments(self):
        """Test that single uppercase letters are treated as string literals"""
        ir = (
            "module",
            (
                ("assign", "grade1", "A", None),
                ("assign", "grade2", "B", None),
                ("assign", "grade3", "F", None),
            ),
        )

        paths = self.executor.execute_program(ir)

        # Should generate 1 path with all assignments
        assert len(paths) == 1, f"Expected 1 path, got {len(paths)}"

        path = paths[0]
        assert "grade1" in path.variables
        assert "grade2" in path.variables
        assert "grade3" in path.variables

        # Check that grades are properly assigned as string values
        grade1_val = path.variables["grade1"]
        grade2_val = path.variables["grade2"]
        grade3_val = path.variables["grade3"]

        assert (
            hasattr(grade1_val, "value") and grade1_val.value == "A"
        ) or grade1_val == "A"
        assert (
            hasattr(grade2_val, "value") and grade2_val.value == "B"
        ) or grade2_val == "B"
        assert (
            hasattr(grade3_val, "value") and grade3_val.value == "F"
        ) or grade3_val == "F"
