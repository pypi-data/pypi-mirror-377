#!/usr/bin/env python3
"""
Z3 Utilities for Symbolic Execution

This module provides utilities for converting AST nodes to Z3 expressions,
handling constraints, and performing satisfiability checking.
"""

import ast
import sys
from typing import Any, Dict, List, Optional, Set, Union
from loguru import logger

# Z3 availability check
try:
    import z3
    from z3 import (
        Solver,
        sat,
        And,
        Or,
        Not,
        IntVal,
        BoolVal,
        RealVal,
        Int,
        Real,
        Bool,
        simplify,
        BoolRef,
        ArithRef,
        BoolSort,
        ToReal,
        Sqrt,
    )

    Z3_AVAILABLE = True
except ImportError as e:
    Z3_AVAILABLE = False
    raise ImportError(f"Z3 is not available: {e}")

logger.remove()  # 移除默认的 handler
logger.add(
    sink=sys.stderr,  # 或 sys.stdout
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{file.path}</cyan>:<cyan>{line}</cyan>:<cyan>{function}</cyan>: - "
        "<level>{message}</level>"
    ),
    colorize=True,
)


def to_z3_expr(expr, var_dict: Optional[Dict[str, Any]] = None):
    """
    Convert various expression types to Z3 expressions.

    Handles: int, float, bool, str, AST nodes, Z3 expressions
    """
    return RangeConstraintGenerator._to_z3_expr(expr, var_dict)


class RangeConstraintGenerator:
    """Generates Z3 constraints for range loop iterations"""

    @staticmethod
    def _to_z3_expr(expr, var_dict: Optional[Dict[str, Any]] = None):
        """Convert various expression types to Z3 expressions"""
        if not Z3_AVAILABLE:
            return None

        if var_dict is None:
            var_dict = {}

        # Direct Z3 expressions
        if hasattr(expr, "sort"):
            return expr

        # Python primitives
        if isinstance(expr, int):
            return IntVal(expr)
        if isinstance(expr, float):
            return RealVal(expr)
        if isinstance(expr, bool):
            return BoolVal(expr)
        if isinstance(expr, str):
            if expr not in var_dict:
                var_dict[expr] = create_z3_variable(expr)
            return var_dict[expr]

        # TODO: support AST nodes
        # if isinstance(expr, ast.AST):
        #     return ast_to_z3_expr(expr, var_dict)

        logger.warning(f"Unsupported expression type:\n {type(expr)}: {expr}")
        return None

    # TODO: check if the constraint is valid
    @staticmethod
    def generate_constraint(
        k: int, start, stop, step=None, var_dict: Optional[Dict[str, Any]] = None
    ):
        """Generate Z3 constraint for the k-th iteration of a range loop"""
        if not Z3_AVAILABLE:
            return None

        if var_dict is None:
            var_dict = {}

        # Convert to Z3 expressions
        # logger.info(f'start: {start} stop: {stop} step: {step}')
        # start_expr = stop_expr = step_expr = None
        start_expr = RangeConstraintGenerator._to_z3_expr(start, var_dict)
        stop_expr = RangeConstraintGenerator._to_z3_expr(stop, var_dict)
        step_expr = RangeConstraintGenerator._to_z3_expr(
            step if step is not None else 1, var_dict
        )

        if None in [start_expr, stop_expr, step_expr]:
            return None

        # Calculate iteration value: start + k * step
        try:
            if start_expr is None or step_expr is None:
                return None
            iter_val = start_expr + IntVal(k) * step_expr
        except Exception:
            return None

        # Determine step direction for constraint generation
        step_const = Z3SafeOperations.extract_constant_value(step_expr)

        constraints = []
        try:
            if step_const is None or step_const > 0:
                # Positive step: iter_val < stop and iter_val >= start
                constraints.append(iter_val < stop_expr)
                constraints.append(iter_val >= start_expr)
            elif step_const < 0:
                # Negative step: iter_val > stop and iter_val <= start
                constraints.append(iter_val > stop_expr)
                constraints.append(iter_val <= start_expr)
            else:
                # Zero step is invalid
                return None

            final_constraint = simplify(And(*constraints))

            # Check satisfiability
            if not Z3SafeOperations.is_sat(final_constraint):
                return None

            return final_constraint
        except Exception:
            return None


# Legacy function wrappers
def simplify_range_cond(
    k: int, start, stop, step=None, var_dict: Optional[Dict[str, Any]] = None
):
    """
    Generate Z3 constraint for the k-th iteration of a range loop.

    Args:
        k: Iteration number (0-based)
        start: Start value (int, AST node, or Z3 expression)
        stop: Stop value (int, AST node, or Z3 expression)
        step: Step value (int, AST node, or Z3 expression), defaults to 1
        var_dict: Dictionary mapping variable names to Z3 variables

    Returns:
        Z3 constraint for the k-th iteration, or None if unsatisfiable
    """
    return RangeConstraintGenerator.generate_constraint(k, start, stop, step, var_dict)


def create_z3_variable(name: str, var_type: str = "int"):
    """Create a Z3 variable of the specified type"""
    return Z3SafeOperations.create_z3_variable(name, var_type)


def extract_constant_value(z3_expr) -> Optional[Union[int, float, bool]]:
    """Extract constant value from Z3 expression if possible"""
    return Z3SafeOperations.extract_constant_value(z3_expr)


class Z3SafeOperations:
    """Safe wrapper for Z3 operations that handles unavailability"""

    @staticmethod
    def create_z3_variable(name: str, var_type: str = "int"):
        """Create a Z3 variable of the specified type"""
        if not Z3_AVAILABLE:
            return name  # Return name if Z3 not available
        var_type = var_type.lower()
        if var_type == "int":
            return Int(name)
        elif var_type == "real":
            return Real(name)
        elif var_type == "bool":
            return Bool(name)
        else:
            return Int(name)  # Default to int

    # TODO: check
    @staticmethod
    def extract_constant_value(z3_expr) -> Optional[Union[int, float, bool]]:
        """Extract constant value from Z3 expression if possible"""
        if not Z3_AVAILABLE or z3_expr is None:
            return None

        try:
            if (
                hasattr(z3, "is_int_value")
                and z3 is not None
                and z3.is_int_value(z3_expr)
            ):
                return z3_expr.as_long()
            elif (
                hasattr(z3, "is_rational_value")
                and z3 is not None
                and z3.is_rational_value(z3_expr)
            ):
                return float(z3_expr.as_decimal(10))
            elif hasattr(z3, "is_bool") and z3 is not None and z3.is_bool(z3_expr):
                return z3.is_true(z3_expr)
        except Exception:
            pass

        return None


def get_vars_from_ast(node: ast.AST) -> Set[str]:
    """Extract all variable names from an AST node"""
    variables = set()

    class VariableCollector(ast.NodeVisitor):
        def visit_Name(self, node):
            variables.add(node.id)
            self.generic_visit(node)

    collector = VariableCollector()
    collector.visit(node)
    return variables


def is_bool(expr):
    """Check if a Z3 expression is boolean type"""
    if expr is None:
        return False
    try:
        return expr.sort() == BoolSort()
    except Exception as e:
        logger.warning(f"Error checking Z3 expression type: {e}")
        return isinstance(expr, bool)


# Legacy function wrappers
def check_path_satisfiability(
    conditions: List[str], var_dict: Optional[Dict[str, Any]] = None
) -> tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if a list of path conditions is satisfiable.

    Returns:
        Tuple of (is_satisfiable, model_values)
    """
    checker = PathSatisfiabilityChecker()
    return checker.check_satisfiability(conditions, var_dict)


class PathSatisfiabilityChecker:
    """Checker for path satisfiability using Z3"""

    def check_satisfiability(
        self, conditions: List[str], var_dict: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a list of path conditions is satisfiable.

        Returns:
            Tuple of (is_satisfiable, model_values)
        """
        if not Z3_AVAILABLE:
            return True, None

        if var_dict is None:
            var_dict = {}

        # try:
        if 1:
            solver = Solver()
            program_variables = set(var_dict.keys())
            # logger.debug(f"program_variables: {program_variables}")

            for condition_str in conditions:
                # try:
                if 1:
                    # constraint = self._parse_condition_string(
                    #     condition_str, var_dict, program_variables
                    # )
                    # logger.debug(f"condition_str: {condition_str}")
                    # logger.debug(f"var_dict: {var_dict}")
                    constraint = to_z3_expr_new(condition_str, var_dict)

                    # Ensure constraint is boolean before adding to solver
                    if constraint is not None:
                        # logger.debug(f"Adding constraint: {constraint} {type(constraint)}")
                        # TODO
                        # bool_constraint = to_bool(constraint)
                        # if bool_constraint is not None:
                        # solver.add(bool_constraint)

                        # Convert integer expressions to boolean comparisons when needed
                        if (
                            z3 is not None
                            and hasattr(z3, "is_expr")
                            and z3.is_expr(constraint)
                        ):
                            # Check if this is a pure integer expression used in boolean context
                            if z3.is_int(constraint) or z3.is_real(constraint):
                                # Convert to boolean comparison (non-zero = True)
                                constraint = constraint != 0
                        else:
                            # logger.debug(f"Constraint is not a Z3 expression: {constraint}")
                            raise ValueError(
                                f"Constraint is not a Z3 expression: {constraint}"
                            )

                        solver.add(constraint)
                    else:
                        # logger.debug(f"Constraint is not a Z3 expression: {constraint}")
                        raise ValueError(
                            f"Constraint is not a Z3 expression: {constraint}"
                        )

                # except Exception as e:
                #     logger.error(f"Error adding constraint for '{condition_str}': {e}")
                #     raise ValueError(f"Error adding constraint for '{condition_str}': {e}")
                # Skip problematic constraints to allow execution to continue

            result = solver.check()
            if result == sat:
                model = solver.model()
                model_values = self._extract_model_values(
                    model, var_dict, program_variables
                )
                return True, model_values
            else:
                return False, None
        # except Exception as e:
        #     logger.error(f"Error checking satisfiability: {e}")
        #     return True, None

    def _extract_model_values(self, model, var_dict, program_variables):
        """Extract model values for program variables"""
        model_values = {}
        for var_name in program_variables:
            if var_name in var_dict and model[var_dict[var_name]] is not None:
                z3_value = model[var_dict[var_name]]
                # Convert Z3 value to Python value
                try:
                    if (
                        hasattr(z3, "is_int_value")
                        and z3 is not None
                        and z3.is_int_value(z3_value)  # IntNumRef
                    ):
                        model_values[var_name] = z3_value.as_long()
                    elif isinstance(z3_value, z3.RatNumRef):
                        num = z3_value.numerator_as_long()
                        den = z3_value.denominator_as_long()
                        if den == 0:  # 表示无穷大
                            return float("inf") if num > 0 else float("-inf")
                        elif den == 1:  # 表示整数
                            model_values[var_name] = num
                        else:
                            # 转换为浮点 same as? float(z3_value.as_fraction())
                            model_values[var_name] = num / den
                    elif (
                        hasattr(z3, "is_bool")
                        and z3 is not None
                        and z3.is_bool(z3_value)
                    ):
                        # raise ValueError("Error parsing Z3 value is_bool")
                        # str(z3.is_true(z3_value)).lower()
                        model_values[var_name] = z3.is_true(z3_value)
                    else:
                        logger.error(
                            f"Error var_name {var_name} z3_value: {z3_value} {type(z3_value)}"
                        )
                        raise ValueError("Error parsing Z3 value others")
                        model_values[var_name] = str(z3_value)
                except Exception as e:
                    logger.error(f"Error parsing Z3 value: {e}")
                    raise ValueError(f"Error parsing Z3 value: {e}")
                    model_values[var_name] = str(z3_value)
        return model_values


def to_z3_expr_new(expr_str, env):
    node = ast.parse(expr_str, mode="eval").body

    def convert(n, bool_context=False):
        if isinstance(n, ast.BinOp):
            left = convert(n.left)
            right = convert(n.right)
            if isinstance(n.op, ast.Add):
                return left + right
            if isinstance(n.op, ast.Sub):
                return left - right
            if isinstance(n.op, ast.Mult):
                return left * right
            if isinstance(n.op, ast.Div):
                return left / right

            if isinstance(n.op, ast.FloorDiv):
                return left / right  # 或 z3.IntDiv(left, right) 更严谨
            if isinstance(n.op, ast.Mod):
                return left % right

            if isinstance(n.op, ast.Pow):
                return left ** right
            # 可选：位运算符
            if isinstance(n.op, ast.LShift):
                return left << right
            if isinstance(n.op, ast.RShift):
                return left >> right
            if isinstance(n.op, ast.BitAnd):
                return left & right
            if isinstance(n.op, ast.BitOr):
                return left | right
            if isinstance(n.op, ast.BitXor):
                return left ^ right

            raise NotImplementedError(f"Unsupported operator: {n.op}")

        elif isinstance(n, ast.Compare):
            left = convert(n.left)
            right = convert(n.comparators[0])
            op = n.ops[0]

            # 如果都是 Python 常量，直接返回 BoolVal
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if isinstance(op, ast.Lt):
                    return BoolVal(left < right)
                if isinstance(op, ast.LtE):
                    return BoolVal(left <= right)
                if isinstance(op, ast.Gt):
                    return BoolVal(left > right)
                if isinstance(op, ast.GtE):
                    return BoolVal(left >= right)
                if isinstance(op, ast.Eq):
                    return BoolVal(left == right)
                if isinstance(op, ast.NotEq):
                    return BoolVal(left != right)

            # BoolRef 与 0/1 比较特殊处理
            if isinstance(left, BoolRef) and isinstance(right, int):
                if isinstance(op, ast.Lt):
                    return left == False if right == 1 else NotImplemented  # noqa: E712
                if isinstance(op, ast.LtE):
                    if right == 0:
                        return left == False  # noqa: E712
                    if right == 1:
                        return True
                if isinstance(op, ast.Gt):
                    return left == True if right == 0 else False  # noqa: E712
                if isinstance(op, ast.GtE):
                    if right == 0:
                        return True
                    if right == 1:
                        return left == True  # noqa: E712
                if isinstance(op, ast.Eq):
                    return left == bool(right)
                if isinstance(op, ast.NotEq):
                    return left != bool(right)

            # 普通比较
            if isinstance(op, ast.Lt):
                return left < right
            if isinstance(op, ast.LtE):
                return left <= right
            if isinstance(op, ast.Gt):
                return left > right
            if isinstance(op, ast.GtE):
                return left >= right
            if isinstance(op, ast.Eq):
                return left == right
            if isinstance(op, ast.NotEq):
                return left != right

        elif isinstance(n, ast.BoolOp):
            values = [convert(v, bool_context=True) for v in n.values]
            if isinstance(n.op, ast.And):
                return And(*values)
            if isinstance(n.op, ast.Or):
                return Or(*values)
        elif isinstance(n, ast.UnaryOp):
            if isinstance(n.op, ast.Not):
                inner = convert(n.operand, bool_context=True)
                if isinstance(inner, ArithRef):
                    return inner == 0
                return Not(inner)
            if isinstance(n.op, ast.USub):
                return -convert(n.operand)
            if isinstance(n.op, ast.UAdd):
                return convert(n.operand)
        elif isinstance(n, ast.Name):
            v = env[n.id]
            if bool_context:
                if isinstance(v, ArithRef):
                    return v != 0
                elif isinstance(v, int):
                    return BoolVal(v != 0)
            return v
        elif isinstance(n, ast.Constant):
            value = n.value
            if bool_context:
                if isinstance(value, int):
                    return BoolVal(value != 0)
                elif isinstance(value, bool):
                    return BoolVal(value)
            return value
        elif isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name) and n.func.id == 'sqrt':
                if len(n.args) == 1:
                    arg = convert(n.args[0])
                    if isinstance(arg, (int, float)):
                        arg = RealVal(arg)
                    elif z3.is_int(arg):
                        arg = ToReal(arg)
                    return Sqrt(arg)
            raise NotImplementedError(f"Unsupported function call: {ast.dump(n)}")
        else:
            raise NotImplementedError(f"Unsupported node: {ast.dump(n)}")

    r = convert(node)
    # ✅ 在这里强制转换 ArithRef 为 BoolRef
    if isinstance(r, ArithRef):
        r = r != 0
    elif isinstance(r, int):
        r = BoolVal(r != 0)

    # logger.debug(f"Converted node: {node} to {r} {type(r)}")
    return r
