import ast
import json
from silu.ir_generator import SiluIRGenerator
from silu.symbolic_executor import SymbolicExecutor
from pprint import pprint

from silu.symbolic_executor import (
    PathCondition,
    ExecutionPath,
)

from silu.symbolic_executor import (
    SymbolicValue,
    SymbolicValueType,
)


src_func_basic = """
def func(x):
    x = 0
    return x
"""


def test_basic():
    source_code = src_func_basic
    tree = ast.parse(source_code)
    ir_generator = SiluIRGenerator()
    ir_result = ir_generator.visit(tree)
    pprint("ir_result:\n")
    pprint(ir_result)

    executor = SymbolicExecutor()
    paths = executor.execute_program(ir_result)

    result = {"paths": paths}
    if hasattr(executor, "function_analyses") and executor.function_analyses:
        result["function_analyses"] = executor.function_analyses

    print(json.dumps(result, indent=2, default=str))
    paths = result["function_analyses"]["func"]

    # Should create multiple paths for different combinations
    assert len(paths) == 1


src_func_nested_if1 = """
def func(x):
    if x > 0:
        if x > 10:
            y = 1
        else:
            y = 2
    else:
        y = 0
    return y
"""


def test_nested_if_1():
    """Test symbolic execution of nested if statements"""
    source_code = src_func_nested_if1
    tree = ast.parse(source_code)
    ir_generator = SiluIRGenerator()
    ir_result = ir_generator.visit(tree)
    pprint("ir_result:\n")
    pprint(ir_result)

    executor = SymbolicExecutor()
    paths = executor.execute_program(ir_result)

    result = {"paths": paths}
    if hasattr(executor, "function_analyses") and executor.function_analyses:
        result["function_analyses"] = executor.function_analyses

    print(json.dumps(result, indent=2, default=str))
    paths = result["function_analyses"]["func"]

    # Should create multiple paths for different combinations
    assert len(paths) == 3


src_func_nested_if2 = """
def func(score):
    if score < 60:
        grade = "F"
    elif score < 70:
        grade = "D"
    elif score < 80:
        grade = "C"
    elif score < 90:
        grade = "B"
    else:
        grade = "A"
    return grade
"""


def test_nested_if_2():
    """Test symbolic execution of nested if statements"""
    source_code = src_func_nested_if2
    tree = ast.parse(source_code)
    ir_generator = SiluIRGenerator()
    ir_result = ir_generator.visit(tree)

    executor = SymbolicExecutor()
    paths = executor.execute_program(ir_result)

    result = {"paths": paths}
    if hasattr(executor, "function_analyses") and executor.function_analyses:
        result["function_analyses"] = executor.function_analyses

    paths = result["function_analyses"]["func"]

    # Should create multiple paths for different combinations
    assert len(paths) == 5


src_func_nested_if3 = """
def func(x):
    if 0 < x < 10:
        return "single_digit"
    elif 10 <= x <= 99:
        return "double_digit"
    elif 100 <= x <= 999:
        return "triple_digit"
    else:
        return "other"
"""


def test_nested_if_3():
    """Test symbolic execution of nested if statements"""
    source_code = src_func_nested_if3
    tree = ast.parse(source_code)
    ir_generator = SiluIRGenerator()
    ir_result = ir_generator.visit(tree)

    executor = SymbolicExecutor()
    paths = executor.execute_program(ir_result)

    result = {"paths": paths}
    if hasattr(executor, "function_analyses") and executor.function_analyses:
        result["function_analyses"] = executor.function_analyses

    paths = result["function_analyses"]["func"]
    # TODO: check test_inputs
    assert len(paths) == 4


def test_add_conditions():
    """Test adding conditions to path"""
    path = ExecutionPath("path_0")
    cond1 = PathCondition("x > 0", True)
    cond2 = PathCondition("x < 10", True)

    path.add_condition(cond1)
    path.add_condition(cond2)

    print(path)
    assert len(path.conditions) == 2
    # 需要变量有定义
    path.variables = {"x": SymbolicValue(SymbolicValueType.CONCRETE, None)}
    assert path.is_satisfiable()


def test_add_conditions2():
    """Test adding conditions to path"""
    path = ExecutionPath("path_0")
    cond1 = PathCondition("x < 0", True)
    cond2 = PathCondition("x > 10", True)

    path.add_condition(cond1)
    path.add_condition(cond2)

    print(path)
    assert len(path.conditions) == 2
    # 需要变量有定义
    path.variables = {"x": SymbolicValue(SymbolicValueType.CONCRETE, None)}
    assert not path.is_satisfiable()


def test_contradictory_conditions():
    """Test contradictory conditions"""
    path = ExecutionPath("path_0")
    cond1 = PathCondition("x > 5", True)
    cond2 = PathCondition("x > 5", False)

    path.add_condition(cond1)
    path.add_condition(cond2)

    path.variables = {"x": SymbolicValue(SymbolicValueType.CONCRETE, None)}

    assert not path.is_satisfiable()


def test_to_dict():
    """Test path serialization"""
    path = ExecutionPath("path_0")
    path.add_condition(PathCondition("x > 5", True))
    path.add_statement("print(x)")

    path.variables = {"x": SymbolicValue(SymbolicValueType.CONCRETE, None)}

    result = path.to_dict()
    assert result["path_id"] == "path_0"
    assert len(result["conditions"]) == 1
    # TODO: : temp disable show statements
    # assert len(result["statements"]) == 1


src_func_while = """
def func(x):
    while x > 0:
        x = x - 1
    return x
"""


def test_while_loop():
    """Test symbolic execution of while loop"""
    # ir_raw = (
    #     "module",
    #     (
    #         (
    #             "while",
    #             ("chained_compare", "x", ">", 0),
    #             ("block", (("assign", "x", ("binary_op", "x", "-", 1), None),)),
    #         ),
    #     ),
    # )

    # executor = SymbolicExecutor()
    # path_id = 'path_a'
    # executor.current_path = ExecutionPath(path_id)
    # executor.current_path.variables = {"x": SymbolicValue(SymbolicValueType.CONCRETE, None)}
    # paths = executor.execute_program(ir)

    source_code = src_func_while
    tree = ast.parse(source_code)
    ir_generator = SiluIRGenerator()
    ir_result = ir_generator.visit(tree)
    pprint("ir_result:\n")
    pprint(ir_result)

    executor = SymbolicExecutor()
    paths = executor.execute_program(ir_result)

    result = {"paths": paths}
    if hasattr(executor, "function_analyses") and executor.function_analyses:
        result["function_analyses"] = executor.function_analyses

    print(json.dumps(result, indent=2, default=str))
    paths = result["function_analyses"]["func"]

    # Should create paths for loop entry and non-entry
    assert len(paths) >= 2


# class TestSymbolicExecutionFromString:
#     """Test symbolic execution from IR strings"""

#     def test_simple_ir_string(self):
#         """Test executing symbolic analysis from IR string"""
#         ir_string = '("module", (("assign", "x", 42, null),))'
#         paths = execute_symbolic_from_string_with_executor(ir_string)["paths"]

#         assert len(paths) == 1
#         # assert "x" in paths[0].variables

#     def test_json_ir_string(self):
#         """Test executing symbolic analysis from JSON IR string"""
#         ir_dict = ["module", [["assign", "x", 42, None]]]
#         ir_string = json.dumps(ir_dict)
#         paths = execute_symbolic_from_string_with_executor(ir_string)["paths"]

#         assert len(paths) == 1
#         # assert "x" in paths[0].variables

#     def test_invalid_ir_string(self):
#         """Test handling of invalid IR string"""
#         with pytest.raises(RuntimeError):
#             execute_symbolic_from_string_with_executor("invalid ir")["paths"]


# def test_execute_symbolic_from_string():
#     """Test symbolic execution from IR string."""

#     # Simple IR for symbolic execution
#     ir_json = json.dumps(
#         [
#             "module",
#             [
#                 ["assign", "x", ["const", 2], None],
#                 [
#                     "if",
#                     [">", ["name", "x"], ["const", 0]],
#                     [["print", ["const", "positive"]]],
#                     [["print", ["const", "non-positive"]]],
#                 ],
#             ],
#         ]
#     )

#     paths = execute_symbolic_from_string_with_executor(ir_json)["paths"]
#     assert len(paths) == 1, f"Expected 1 paths, got {len(paths)}"


# def test_merge_negative_conditions_basic():
#     """Test basic merging of negative conditions"""
#     # Test case: not (x > 10) and not (x > 0) should become x <= 0
#     conditions = [
#         PathCondition("x > 10", False),  # not (x > 10)
#         PathCondition("x > 0", False),  # not (x > 0)
#     ]

#     merged = self.executor._merge_negative_conditions("x", conditions)

#     assert len(merged) == 1
#     assert merged[0].expression == "x <= 0.0"
#     assert merged[0].is_true is True

# def test_merge_negative_conditions_multiple_values():
#     """Test merging with multiple comparison values"""
#     # Test case: not (x > 15), not (x > 10), not (x > 5) should become x <= 5
#     conditions = [
#         PathCondition("x > 15", False),
#         PathCondition("x > 10", False),
#         PathCondition("x > 5", False),
#     ]

#     merged = self.executor._merge_negative_conditions("x", conditions)

#     assert len(merged) == 1
#     assert merged[0].expression == "x <= 5.0"
#     assert merged[0].is_true is True

# def test_merge_negative_conditions_no_merge_needed():
#     """Test that single conditions are not unnecessarily changed"""
#     conditions = [
#         PathCondition("x > 5", False),
#     ]

#     merged = self.executor._merge_negative_conditions("x", conditions)

#     assert len(merged) == 1
#     assert merged == conditions  # Should return original

# def test_merge_negative_conditions_non_numeric():
#     """Test handling of non-numeric comparison values"""
#     conditions = [
#         PathCondition("x > variable_y", False),
#         PathCondition("x > 10", False),
#     ]

#     # Should return original conditions when non-numeric values are present
#     merged = self.executor._merge_negative_conditions("x", conditions)
#     assert merged == conditions
