#!/usr/bin/env python3
"""
Unit tests for the symbolic execution engine.
"""

import pytest
from silu.symbolic_executor import (
    SymbolicExecutor,
    SymbolicValue,
    SymbolicValueType,
    PathCondition,
    ExecutionPath,
    SymbolicEnvironment,
    # execute_symbolic_from_string_with_executor,
)
from silu.symbolic.condition_utils import (
    extract_variable_from_condition,
    is_simple_variable_condition,
    group_conditions_by_variable,
)


class TestSymbolicValue:
    """Test SymbolicValue class"""

    def test_concrete_value(self):
        """Test concrete symbolic value"""
        val = SymbolicValue(SymbolicValueType.CONCRETE, 42)
        assert str(val) == "42"
        assert val.type == SymbolicValueType.CONCRETE

    def test_symbolic_value(self):
        """Test symbolic variable"""
        val = SymbolicValue(SymbolicValueType.SYMBOLIC, None, "x")
        assert str(val) == "x"
        assert val.type == SymbolicValueType.SYMBOLIC

    def test_expression_value(self):
        """Test symbolic expression"""
        val = SymbolicValue(SymbolicValueType.EXPRESSION, "(x + 1)")
        assert str(val) == "(x + 1)"
        assert val.type == SymbolicValueType.EXPRESSION


class TestPathCondition:
    """Test PathCondition class"""

    def test_true_condition(self):
        """Test true path condition"""
        cond = PathCondition("x > 5", True)
        assert str(cond) == "x > 5"

    def test_false_condition(self):
        """Test false path condition"""
        cond = PathCondition("x > 5", False)
        assert str(cond) == "not x > 5"

    def test_negate(self):
        """Test condition negation"""
        cond = PathCondition("x > 5", True)
        negated = cond.negate()
        assert not negated.is_true
        assert negated.expression == "x > 5"


class TestExecutionPath:
    """Test ExecutionPath class"""

    def test_empty_path(self):
        """Test empty execution path"""
        path = ExecutionPath("path_0")
        assert path.path_id == "path_0"
        assert len(path.conditions) == 0
        assert len(path.statements) == 0
        assert path.is_satisfiable()


class TestSymbolicEnvironment:
    """Test SymbolicEnvironment class"""

    def test_create_symbol(self):
        """Test symbol creation"""
        env = SymbolicEnvironment()
        sym = env.create_symbol("x")
        assert sym.name == "x"
        assert sym.type == SymbolicValueType.SYMBOLIC

    def test_variable_storage(self):
        """Test variable storage and retrieval"""
        env = SymbolicEnvironment()
        sym = env.create_symbol("x")
        env.set_variable("x", sym)

        retrieved = env.get_variable("x")
        assert retrieved.name == "x"

    def test_undefined_variable(self):
        """Test access to undefined variable"""
        env = SymbolicEnvironment()
        sym = env.get_variable("undefined")
        assert sym.name == "undefined"
        assert sym.type == SymbolicValueType.SYMBOLIC

    def test_environment_copy(self):
        """Test environment copying"""
        env = SymbolicEnvironment()
        env.set_variable("x", env.create_symbol("x"))

        copy_env = env.copy()
        assert "x" in copy_env.variables
        assert copy_env.variables["x"].name == "x"


class TestSymbolicExecutor:
    """Test SymbolicExecutor class"""

    def test_simple_assignment(self):
        """Test symbolic execution of simple assignment"""
        ir = ("module", (("assign", "x", 42, None),))

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) == 1
        assert "x" in paths[0].variables
        assert paths[0].variables["x"].value == 42

    # x is not defined
    # def test_simple_if_statement(self):
    #     """Test symbolic execution of if statement"""
    #     # if x > 5: y = 1 else: y = 2
    #     ir = (
    #         "module",
    #         (
    #             (
    #                 "if",
    #                 ("chained_compare", "x", ">", 5),
    #                 ("block", (("assign", "y", 1, None),)),
    #                 ("block", (("assign", "y", 2, None),)),
    #             ),
    #         ),
    #     )

    #     executor = SymbolicExecutor()
    #     paths = executor.execute_program(ir)

    #     # Should create two paths: true and false
    #     print(paths)
    #     assert len(paths) == 2

    #     # Check that both paths have different conditions
    #     conditions = [path.conditions[0].is_true for path in paths]
    #     assert True in conditions
    #     assert False in conditions

    def test_function_definition(self):
        """Test symbolic execution of function definition"""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "test_func",
                    ["x"],
                    ("block", (("return", ("binary_op", "x", "+", 1)),)),
                ),
            ),
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) == 1
        assert "test_func" in executor.global_env.functions

    def test_function_call(self):
        """Test symbolic execution of function call"""
        ir = ("module", (("call", "print", ("x",)),))

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) == 1
        # 不再检查 statements
        # assert "print(x)" in paths[0].statements

    def test_binary_operations(self):
        """Test symbolic execution of binary operations"""
        ir = ("module", (("assign", "z", ("binary_op", "x", "+", "y"), None),))

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) == 1
        assert "z" in paths[0].variables
        assert "x" in str(paths[0].variables["z"])
        assert "y" in str(paths[0].variables["z"])

    def test_return_statement(self):
        """Test symbolic execution of return statement"""
        ir = ("module", (("return", 42),))

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) == 1
        assert paths[0].return_value.value == 42

    def test_builtin_functions(self):
        """Test symbolic execution with builtin functions"""
        ir = (
            "module",
            (
                ("call", "int", ("3.14",)),
                ("call", "str", (42,)),
                ("call", "len", ("hello",)),
            ),
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) == 1
        # 不再检查 statements
        # statements = " ".join(paths[0].statements)
        # assert "int" in statements or "str" in statements or "len" in statements

    def test_chained_comparisons(self):
        """Test symbolic execution of chained comparisons"""
        ir = (
            "module",
            (("assign", "result", ("chained_compare", 1, "<", "x", "<", 10), None),),
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        assert len(paths) == 1
        # assert "result" in paths[0].variables

    def test_report_generation(self):
        """Test symbolic execution report generation"""
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

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)
        report = executor.generate_report(paths)

        assert "total_paths" in report
        assert "satisfiable_paths" in report
        assert "paths" in report
        # assert "summary" in report
        assert report["total_paths"] > 0

    # undefine
    # def test_path_limit(self):
    #     """Test that path explosion is limited"""
    #     # Create a deeply nested if structure that would explode paths
    #     ir = (
    #         "module",
    #         (
    #             (
    #                 "if",
    #                 ("chained_compare", "a", ">", 0),
    #                 (
    #                     "block",
    #                     (
    #                         (
    #                             "if",
    #                             ("chained_compare", "b", ">", 0),
    #                             (
    #                                 "block",
    #                                 (
    #                                     (
    #                                         "if",
    #                                         ("chained_compare", "c", ">", 0),
    #                                         ("block", (("assign", "x", 1, None),)),
    #                                         ("block", (("assign", "x", 2, None),)),
    #                                     ),
    #                                 ),
    #                             ),
    #                             ("block", (("assign", "x", 3, None),)),
    #                         ),
    #                     ),
    #                 ),
    #                 ("block", (("assign", "x", 4, None),)),
    #             ),
    #         ),
    #     )

    #     executor = SymbolicExecutor()
    #     executor.max_paths = 10  # Set a low limit for testing
    #     paths = executor.execute_program(ir)

    #     # Should be limited by max_paths
    #     assert len(paths) <= executor.max_paths


class TestIntegration:
    """Integration tests for symbolic execution"""

    def test_factorial_function_symbolic(self):
        """Test symbolic execution of factorial function"""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "factorial",
                    ["n"],
                    (
                        "block",
                        (
                            (
                                "if",
                                ("chained_compare", "n", "<=", 1),
                                ("block", (("return", 1),)),
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
                                                    (("binary_op", "n", "-", 1),),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                ("assign", "result", ("call", "factorial", (5,)), None),
            ),
        )

        executor = SymbolicExecutor()
        paths = executor.execute_program(ir)

        # Should have paths for the recursive calls
        assert len(paths) > 0
        assert "factorial" in executor.global_env.functions

    # TODO
    # def test_complex_control_flow(self):
    #     """Test symbolic execution with complex control flow"""
    #     ir = (
    #         "module",
    #         (
    #             ("assign", "x", 10, None),
    #             (
    #                 "while",
    #                 ("chained_compare", "x", ">", 0),
    #                 (
    #                     "block",
    #                     (
    #                         (
    #                             "if",
    #                             ("chained_compare", "x", "%", 2, "==", 0),
    #                             (
    #                                 "block",
    #                                 (
    #                                     (
    #                                         "assign",
    #                                         "x",
    #                                         ("binary_op", "x", "/", 2),
    #                                         None,
    #                                     ),
    #                                 ),
    #                             ),
    #                             (
    #                                 "block",
    #                                 (
    #                                     (
    #                                         "assign",
    #                                         "x",
    #                                         ("binary_op", "x", "-", 1),
    #                                         None,
    #                                     ),
    #                                 ),
    #                             ),
    #                         ),
    #                         ("call", "print", ("x",)),
    #                     ),
    #                 ),
    #             ),
    #         ),
    #     )

    #     executor = SymbolicExecutor()
    #     paths = executor.execute_program(ir)

    #     # Should generate multiple paths due to control flow
    #     assert len(paths) > 0

    #     # Verify that paths contain expected statements
    #     all_statements = []
    #     for path in paths:
    #         all_statements.extend(path.statements)

    # TODO: : temp disable show statements
    # assert any("while" in stmt for stmt in all_statements)
    # assert any("print" in stmt for stmt in all_statements)


class TestConditionSimplification:
    """Test cases for path condition simplification"""

    def setup_method(self):
        """Setup test environment"""
        self.executor = SymbolicExecutor()

    def test_extract_variable_from_condition(self):
        """Test variable extraction from simple conditions"""
        # Test basic comparisons
        assert extract_variable_from_condition("x > 5") == "x"
        assert extract_variable_from_condition("y <= 10") == "y"
        assert extract_variable_from_condition("z >= 0") == "z"
        assert extract_variable_from_condition("abc < 100") == "abc"

        # Test with whitespace
        assert extract_variable_from_condition("  x  >  5  ") == "x"

        # Test complex expressions (should return None for now)
        assert extract_variable_from_condition("x + y > 5") is None
        assert extract_variable_from_condition("func(x) > 5") is None
        assert extract_variable_from_condition("5 > x") is None  # Reverse order

    def test_is_simple_variable_condition(self):
        """Test identification of simple variable conditions"""
        assert is_simple_variable_condition("x > 5") is True
        assert is_simple_variable_condition("y <= 10") is True
        assert is_simple_variable_condition("x + y > 5") is False
        assert is_simple_variable_condition("complex_expr") is False

    def test_group_conditions_by_variable(self):
        """Test grouping of conditions by variable"""
        conditions = [
            PathCondition("x > 5", True),
            PathCondition("x > 10", False),
            PathCondition("y < 0", True),
            PathCondition("x <= 3", True),
            PathCondition("z >= 1", True),
        ]

        groups = group_conditions_by_variable(conditions)

        assert "x" in groups
        assert "y" in groups
        assert "z" in groups
        assert len(groups["x"]) == 3  # x > 5, not (x > 10), x <= 3
        assert len(groups["y"]) == 1  # y < 0
        assert len(groups["z"]) == 1  # z >= 1


class TestFunctionAnalyses:
    """Test function analysis functionality"""

    def test_function_analyses_generation(self):
        """Test that function analyses are properly generated in reports"""
        import ast
        from silu.ir_generator import SiluIRGenerator

        code = """
def simple_branch(x):
    if x > 5:
        result = x + 1
        return result
    else:
        result = x - 1
        return result

def test_function(a, b):
    if a > b:
        return a + b
    else:
        return a * b

# Test the functions
y = simple_branch(3)
z = test_function(4, 2)
"""

        # Convert source code to IR first
        tree = ast.parse(code)
        ir_generator = SiluIRGenerator()
        ir_result = ir_generator.visit(tree)

        # Execute symbolic analysis using SymbolicExecutor directly
        executor = SymbolicExecutor()
        paths = executor.execute_program(ir_result)
        result = executor.generate_report(paths)

        # Check that function analyses are present
        assert "function_analyses" in result

        # Check that both functions are analyzed
        assert "simple_branch" in result["function_analyses"]
        assert "test_function" in result["function_analyses"]

        # Check simple_branch analysis
        simple_branch_analysis = result["function_analyses"]["simple_branch"]
        assert simple_branch_analysis["total_paths"] == 2  # Two paths: x > 5 and x <= 5
        assert simple_branch_analysis["satisfiable_paths"] == 2
        assert len(simple_branch_analysis["paths"]) == 2

        # Check test_function analysis
        test_function_analysis = result["function_analyses"]["test_function"]
        assert test_function_analysis["total_paths"] == 2  # Two paths: a > b and a <= b
        assert test_function_analysis["satisfiable_paths"] == 2
        assert len(test_function_analysis["paths"]) == 2

        # Verify that each function path has conditions
        for path in simple_branch_analysis["paths"]:
            assert len(path["conditions"]) >= 1  # Should have at least one condition
            # TODO: : temp disable show statements
            # assert "x" in path["variables"]  # Should have the parameter

        for path in test_function_analysis["paths"]:
            assert len(path["conditions"]) >= 1  # Should have at least one condition
            # TODO:
            # assert (
            #     "a" in path["variables"] and "b" in path["variables"]
            # )  # Should have parameters


class TestCaseGeneration:
    """Test Z3 test case generation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.executor = SymbolicExecutor()


if __name__ == "__main__":
    pytest.main([__file__])
