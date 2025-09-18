#!/usr/bin/env python3
"""
Enhanced Symbolic Execution Engine for Silu Language

This module provides symbolic execution capabilities for Silu programs,
allowing analysis of all possible execution paths and generation of
path constraints for functions with improved Z3 integration and loop handling.
"""

import copy
from typing import Any, Dict, List, Tuple, Optional, Union

# Import symbolic execution utilities
from .symbolic_utils import logger

from .symbolic.loop_utils import LoopAnalyzer
from .symbolic.condition_utils import PathCondition
from .symbolic.report_utils import generate_comprehensive_report
from .symbolic_pathlib import PathManager, ExecutionPath

from .symbolic_utils import (
    Config,
    ExecutionPathState,
    SymbolicEnvironment,
    AssignmentHandler,
    ConditionalHandler,
    LoopHandler,
)
from .symbolic.builtin_utils import (
    SymbolicValueType,
    SymbolicValue,
    create_concrete_value,
    create_symbolic_value,
    create_expression_value,
    create_builtin_functions_dict,
)


# Helper functions for symbolic value type checking
def is_symbolic(value: SymbolicValue) -> bool:
    """Check if a value is symbolic (not concrete)"""
    return hasattr(value, "type") and (
        value.type == SymbolicValueType.SYMBOLIC
        or value.type == SymbolicValueType.EXPRESSION
    )


class SymbolicExecutor:
    """Enhanced symbolic execution engine for Silu IR with improved architecture"""

    def __init__(
        self,
        performance_mode: bool = False,
        debug: bool = False,
    ):
        # Configure limits based on mode
        max_paths = (
            Config.PERFORMANCE_MAX_PATHS
            if performance_mode
            else Config.DEFAULT_MAX_PATHS
        )
        self.path_manager = PathManager(max_paths)
        self.performance_mode = performance_mode
        self.global_env = SymbolicEnvironment()
        self.enum_types = {}  # Store enum type definitions

        self.current_path: Optional[ExecutionPath] = None
        self.current_env = self.global_env
        self.function_analyses: Dict[str, List[ExecutionPath]] = {}

        self.debug = debug
        self.max_loop_iterations = (
            Config.PERFORMANCE_MAX_LOOP_ITERATIONS
            if performance_mode
            else Config.DEFAULT_MAX_LOOP_ITERATIONS
        )
        self.loop_analyzer = LoopAnalyzer(max_iterations=self.max_loop_iterations)

        # 初始化链式比较处理标志
        # 此标志用于避免在处理链式比较（如 0 < x < 10）时
        # 同时在 _execute_binary_op 和 _execute_chained_compare 中重复添加条件
        self._processing_chained_compare = False

        # # Initialize handlers
        self._init_handlers()
        # # Initialize built-in functions
        self._init_builtins()

    def execute_program(self, ir_program: Tuple) -> List[ExecutionPath]:
        """Execute an IR program symbolically and return all paths"""
        if not ir_program or ir_program[0] != "module":
            raise ValueError("Invalid IR program format")

        self.current_path = self.path_manager.create_path()
        self.current_path._function_params = []  # 添加函数参数列表

        self._execute_ir(ir_program)

        if self.current_path:
            self.path_manager.add_path(self.current_path)

        paths = copy.deepcopy(self.path_manager.finalize_paths())
        # TODO: why renumber_paths_sequentially the paths out of finalize_paths is not good
        # paths = self.path_manager.paths
        # paths = renumber_paths_sequentially(paths)
        return paths

    def generate_report(self, paths: List[ExecutionPath]) -> Dict[str, Any]:
        """Generate a comprehensive report of symbolic execution results"""

        report = generate_comprehensive_report(
            paths=paths,
            performance_mode=self.performance_mode,
            global_env_functions=self.global_env.functions,
            function_analyses=getattr(self, "function_analyses", None),
        )
        return report

    def _init_handlers(self):
        """Initialize IR node handlers"""
        self.handlers = [
            AssignmentHandler(),
            ConditionalHandler(),
            LoopHandler(),
        ]

    def _init_builtins(self):
        """Initialize built-in functions"""
        builtins = create_builtin_functions_dict(current_path=self.current_path)
        self.global_env.functions.update(builtins)

    def _execute_ir(self, ir_node: Union[Tuple, str, Any]) -> SymbolicValue:
        """Execute an IR node and return its symbolic value

        Execution flow:
        1. Handle non-tuple nodes (primitives, strings, etc.)
        2. Unwrap single-element tuples if needed
        3. Try specialized handlers first (AssignmentHandler, ConditionalHandler, LoopHandler)
        4. Fallback to direct dispatch for other operations
        """

        if not isinstance(ir_node, (tuple, list)) or not ir_node:
            # Handle primitive values, strings, and empty nodes
            return self._handle_non_tuple_node(ir_node)

        # Handle wrapped statements - if we have a single-element tuple containing a statement
        # unwrap it to the actual statement
        # This handles cases like [["return", value]] -> ["return", value]
        if (
            isinstance(ir_node, tuple)
            and len(ir_node) == 1
            and isinstance(ir_node[0], tuple)
            and len(ir_node[0]) > 0
            and isinstance(ir_node[0][0], str)
        ):
            unwrapped = ir_node[0]
            return self._execute_ir(unwrapped)

        # Try specialized handlers first:
        # - AssignmentHandler: handles "=" operations
        # - ConditionalHandler: handles "if" statements with path forking
        # - LoopHandler: handles "while", "for", "c_for" loops
        for handler in self.handlers:
            if handler.can_handle(ir_node):
                return handler.handle(ir_node, self)

        # Fallback to direct dispatch for other operations:
        # - Arithmetic: +, -, *, /, etc.
        # - Comparisons: ==, !=, <, >, etc.
        # - Function calls, returns, blocks, etc.
        return self._dispatch_ir_node(ir_node)

    def _set_processing_chained_compare(self, value: bool) -> None:
        """
        设置链式比较处理标志

        在处理链式比较前后设置此标志，以防止条件被重复添加

        参数:
            value (bool): 标志的新值
        """
        self._processing_chained_compare = value

    def _dispatch_ir_node(self, ir_node: Tuple) -> SymbolicValue:
        """Dispatch IR node to appropriate handler method

        This handles operations that are not covered by specialized handlers:
        - Binary operations: +, -, *, /, ==, !=, <, >, and, or, etc.
        - Function operations: func_def, call, return
        - Control flow: block (statement sequences)
        - Data access: name (variables), const (constants), literal
        - Type operations: typedef_enum, typedef_struct, attribute
        - C-style operations: p++, p--, ++, --, aug_assign, c_for

        Note: "if" statements are handled by ConditionalHandler, not here.
        """
        op = ir_node[0]

        # Binary operations that should use _execute_binary_op
        binary_ops = {
            "+",
            "-",
            "*",
            "/",
            "//",
            "%",
            "**",
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
            "and",
            "or",
            "not",
        }

        dispatch_table = {
            "module": self._execute_module,
            "name": self._execute_name,
            "const": self._execute_const,
            "literal": self._execute_literal,
            "func_def": self._execute_func_def,
            "call": self._execute_call,
            "return": self._execute_return,
            "block": self._execute_block,
            "binary_op": self._execute_binary_op,
            "chained_compare": self._execute_chained_compare,
            "comparison": self._execute_comparison,
            "match": self._execute_match,
            "switch": self._execute_switch,
            "c_for": self._execute_c_for,
            "p++": self._execute_post_increment,
            "p--": self._execute_post_decrement,
            "++": self._execute_pre_increment,
            "--": self._execute_pre_decrement,
            "aug_assign": self._execute_aug_assign,
            "print": self._execute_print,
            "binop": self._execute_binop,
            "typedef_enum": self._execute_typedef_enum,
            "typedef": self._execute_typedef,
            "typedef_struct": self._execute_typedef_struct,
            "attribute": self._execute_attribute,
            # Add a fallback handler for any missing operations
            "__missing__": lambda ir_node: create_symbolic_value(
                f"unimplemented_{ir_node[0]}"
            ),
        }

        # Add binary operations to dispatch table
        for binary_op in binary_ops:
            dispatch_table[binary_op] = self._execute_binary_op

        try:
            if op in dispatch_table:
                return dispatch_table[op](ir_node)
            elif isinstance(op, str) and op.isdigit():
                # Handle integer literals
                return create_concrete_value(int(op))
            elif isinstance(op, str):
                # Try to handle as variable reference
                if self.current_env.has_variable(op):
                    return self.current_env.get_variable(op)
                # Create a symbolic value for unknown variables
                return create_symbolic_value(f"unknown_{op}")
            else:
                # Fallback for other cases
                return create_concrete_value(op)
        except Exception as e:
            logger.error(f"Error dispatching operation {op}: {e}")
            import traceback

            logger.error(traceback.format_exc())
            # Return a fallback symbolic value
            return create_symbolic_value(f"error_{op}")

    def _execute_module(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a module IR node"""
        for stmt in ir_node[1]:
            self._execute_ir(stmt)
        return create_concrete_value(None)

    def _execute_name(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a name (variable reference) IR node"""
        _, var_name = ir_node
        # 优先检查当前路径中的变量（可能包含更新的值）
        if self.current_path and var_name in self.current_path.variables:
            return self.current_path.variables[var_name]
        # 检查变量是否在当前环境中
        if self.current_env.has_variable(var_name):
            return self.current_env.get_variable(var_name)
        # 如果变量不存在，创建一个符号变量
        # 这样可以确保即使变量尚未定义，我们也能得到一个有效的符号名
        symbol = self.current_env.create_symbol(var_name)
        self.current_env.set_variable(var_name, symbol)
        return symbol

    def _execute_const(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a constant IR node"""
        _, value = ir_node
        result = create_concrete_value(value)
        result.original_ir = ir_node
        return result

    def _execute_typedef_enum(self, ir_node: Tuple) -> SymbolicValue:
        """Execute enum type definition with constants."""
        # Extract enum name and constants from IR node
        _, enum_name, constants = ir_node

        # Store the enum type
        self.enum_types[enum_name] = "enum"

        # Define each enum constant as a variable
        for constant_name, value_ir in constants:
            # Execute the value IR (typically ["const", value])
            value = self._execute_ir(value_ir)
            self.current_env.variables[constant_name] = value

        # Return None as this operation doesn't produce a value
        return create_concrete_value(None)

    def _execute_typedef(self, ir_node: Tuple) -> SymbolicValue:
        """Execute type definition."""
        # Extract type name and type specification from IR node
        _, name, type_spec = ir_node

        if type_spec == "Enum":
            # Store the enum type
            self.enum_types[name] = type_spec
        elif (
            isinstance(type_spec, tuple)
            and len(type_spec) >= 2
            and type_spec[0] == "Enum"
        ):
            # Future extensibility: Handle enum with constants list
            # Format: ("Enum", [constant_names])
            self.enum_types[name] = type_spec[0]
        else:
            # Store the typedef mapping for other types
            self.current_env.variable_types[name] = type_spec

            # Handle other typedef cases (like struct)
            if isinstance(type_spec, str) and hasattr(
                self, f"_execute_typedef_{type_spec.lower()}"
            ):
                getattr(self, f"_execute_typedef_{type_spec.lower()}")(name, type_spec)

        # Return None as this operation doesn't produce a value
        return create_concrete_value(None)

    def _execute_typedef_struct(self, ir_node: Tuple) -> SymbolicValue:
        """Execute struct type definition."""
        try:
            # Extract struct name and fields from IR node
            _, name, fields = ir_node

            # Store the struct type definition
            if not hasattr(self, "struct_types"):
                self.struct_types = {}
            self.struct_types[name] = fields

            # Return None as this operation doesn't produce a value
            return create_concrete_value(None)
        except Exception as e:
            logger.error(f"Error in _execute_typedef_struct: {e}")
            # Still initialize struct_types if needed
            if not hasattr(self, "struct_types"):
                self.struct_types = {}
            # Return None for error case
            return create_concrete_value(None)

    def _execute_attribute(self, ir_node: Tuple) -> SymbolicValue:
        """Execute attribute access obj.attr."""
        try:
            # Extract object and attribute from IR node
            _, obj, attr = ir_node

            # Execute object IR to get the object value
            obj_val = self._execute_ir(obj)

            # For symbolic execution, we'll create a new symbolic value representing the attribute access
            if is_symbolic(obj_val):
                # Create a symbolic representation of the attribute access
                obj_name = self._extract_variable_name(obj)
                if obj_name:
                    return create_symbolic_value(f"{obj_name}.{attr}")
                return create_symbolic_value(f"attribute_access.{attr}")

            # If it's a struct type, create a placeholder value for the field
            if hasattr(self, "struct_types"):
                obj_str = (
                    str(obj_val.value) if hasattr(obj_val, "value") else str(obj_val)
                )

                # Check if this is a struct instance
                for struct_name, fields in self.struct_types.items():
                    struct_id = f"struct_{struct_name}"
                    if struct_id == obj_str:
                        # Find the field in this struct
                        for field_name, field_type in fields:
                            if field_name == attr:
                                # Create a default value for this field type
                                if field_type == "int":
                                    return create_concrete_value(0)
                                elif field_type == "float":
                                    return create_concrete_value(0.0)
                                elif field_type == "char*" or field_type == "string":
                                    return create_concrete_value("")
                                else:
                                    return create_symbolic_value(f"{struct_id}.{attr}")

            # For concrete execution, try to access the attribute
            if (
                hasattr(obj_val, "value")
                and isinstance(obj_val.value, dict)
                and attr in obj_val.value
            ):
                return create_concrete_value(obj_val.value[attr])

            # Default to a symbolic value when we can't determine the concrete value
            return create_symbolic_value(f"sym_{attr}")
        except Exception as e:
            logger.error(f"Error in _execute_attribute: {e}")
            # Return a fallback symbolic value for the attribute
            return create_symbolic_value(f"error_attr_{attr}")

    def _execute_literal(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a literal IR node"""
        if len(ir_node) > 1:
            return create_concrete_value(ir_node[1])
        return create_concrete_value(None)

    def _execute_func_def(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a function definition"""
        # Handle both Silu format (4 elements) and C format (5-6 elements)
        param_types = return_type = None
        if len(ir_node) == 4:
            # Silu format: ("func_def", name, params, body)
            _, func_name, params, body = ir_node
        elif len(ir_node) >= 5:
            # C format: ("func_def", name, params, body, param_types, [return_type])
            _, func_name, params, body = ir_node[:4]
            param_types = ir_node[4]
            return_type = ir_node[5]
        else:
            raise ValueError(
                f"Invalid func_def format: expected 4+ elements, got {len(ir_node)}"
            )
        self.global_env.functions[func_name] = (params, body)

        if self.current_path:
            params_str = ", ".join(params) if params else ""
            self.current_path.add_statement(f"def {func_name}({params_str}):")

        # Always analyze function for reporting purposes
        function_paths = self._analyze_function_definition(
            func_name, params, body, param_types, return_type
        )
        self.function_analyses[func_name] = function_paths

        return create_concrete_value(None)

    def _execute_call(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a function call symbolically"""
        # logger.warning(f"ir_node of _execute_call: {ir_node}")
        if len(ir_node) == 4:
            _, func_name, args_ir, kwargs_ir = ir_node
        else:
            _, func_name, args_ir = ir_node

        if isinstance(func_name, (list, tuple)) and func_name[0] == 'name':
            func_name = func_name[1]

        args = [self._execute_ir(arg) for arg in args_ir]

        # 记录函数调用语句，不管是否为内置函数
        if self.current_path:
            args_str = ", ".join(self._convert_value_display(arg) for arg in args)
            self.current_path.add_statement(f"{func_name}({args_str})")

        if func_name in self.global_env.functions:
            func_handler = self.global_env.functions[func_name]
            if callable(func_handler):
                # Built-in function
                result = func_handler(*args)
                return result
            else:
                # User-defined function - create symbolic return value
                return_symbol = self.current_env.create_symbol(f"{func_name}_return")
                if self.current_path:
                    args_str = ", ".join(str(arg) for arg in args)
                    self.current_path.add_statement(
                        f"{return_symbol} = {func_name}({args_str})"
                    )
                return return_symbol
        else:
            # Unknown function
            result = self.current_env.create_symbol(f"unknown_{func_name}")
            if self.current_path:
                args_str = ", ".join(str(arg) for arg in args)
                self.current_path.add_statement(
                    f"{result} = {func_name}({args_str}) # unknown function"
                )
            return result

    def _execute_return(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a return statement"""
        if len(ir_node) > 1:
            value = self._execute_ir(ir_node[1])
        else:
            value = create_concrete_value(None)

        if self.current_path:
            self.current_path.return_value = value
            self.current_path.add_statement(f"return {self._simplify_display(value)}")
            self.current_path.state = ExecutionPathState.COMPLETED

        return value

    def _execute_block(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a block of statements"""
        result = create_concrete_value(None)
        if len(ir_node) > 1:
            statements = ir_node[1]
            # If statements is a tuple/list, iterate through it
            if isinstance(statements, (tuple, list)):
                for stmt in statements:
                    result = self._execute_ir(stmt)
            else:
                # Single statement
                result = self._execute_ir(statements)
        return result

    def _execute_binary_op(self, ir_node: Tuple) -> SymbolicValue:
        """Execute binary operations with enhanced Z3 constraint generation"""
        try:
            # 解析二元操作的左右操作数
            left_ir = None
            right_ir = None
            if len(ir_node) == 4:
                _, left_ir, op, right_ir = ir_node
                left = self._execute_ir(left_ir)
                right = self._execute_ir(right_ir)
            elif len(ir_node) == 3:
                op, left_ir, right_ir = ir_node
                left = self._execute_ir(left_ir)
                right = self._execute_ir(right_ir)
            elif len(ir_node) == 2:
                op, operand_ir = ir_node
                operand = self._execute_ir(operand_ir)
                return create_expression_value((op, operand))
            else:
                return create_concrete_value(None)

            # Always create symbolic expressions for operations involving symbolic variables
            # This prevents boolean casting errors
            if (
                left.type == SymbolicValueType.SYMBOLIC
                or right.type == SymbolicValueType.SYMBOLIC
                or left.type == SymbolicValueType.EXPRESSION
                or right.type == SymbolicValueType.EXPRESSION
            ):
                # 对于and操作，我们已经单独处理了条件添加
                expr = (op, left, right)
                return create_expression_value(expr)

            # Try concrete evaluation only if both operands are concrete
            if (
                left.type == SymbolicValueType.CONCRETE
                and right.type == SymbolicValueType.CONCRETE
            ):
                concrete_result = self._try_concrete_operation(
                    op, left.value, right.value
                )
                if concrete_result is not None:
                    return create_concrete_value(concrete_result)

            # Default to symbolic expression
            expr = (op, left, right)
            return create_expression_value(expr)

        except Exception as e:
            logger.error(f"Error: {e}")
            # Create a symbolic expression as fallback to avoid errors
            if len(ir_node) >= 3:
                if len(ir_node) == 4:
                    _, left_ir, op, right_ir = ir_node
                else:
                    op, left_ir, right_ir = ir_node
                # Create fallback symbolic expression
                left_sym = create_symbolic_value(str(left_ir))
                right_sym = create_symbolic_value(str(right_ir))
                expr = (op, left_sym, right_sym)
                return create_expression_value(expr)

            if self.current_path:
                self.current_path.add_statement(f"Error in binary operation: {e}")
                self.current_path.state = ExecutionPathState.ERROR
            return create_concrete_value(None)

    def _extract_variable_name(self, ir_node: Any) -> Optional[str]:
        """从IR节点中提取变量名"""
        if isinstance(ir_node, tuple) and len(ir_node) >= 2:
            if ir_node[0] == "name":
                return ir_node[1]  # 返回变量名
            elif len(ir_node) >= 3 and ir_node[0] in ["<", "==", ">", "<=", ">=", "!="]:
                # 递归处理比较操作的左右操作数
                left_name = self._extract_variable_name(ir_node[1])
                right_name = self._extract_variable_name(ir_node[2])
                if left_name:
                    return left_name
                return right_name
        return None

    def _try_concrete_operation(
        self, op: str, left_val: Any, right_val: Any
    ) -> Optional[Any]:
        """Try to perform concrete operation"""
        try:
            # Skip operations with tuples (expression values) or None values
            if isinstance(left_val, tuple) or isinstance(right_val, tuple):
                return None
            if left_val is None or right_val is None:
                return None

            operations = {
                "+": lambda a, b: a + b,
                "-": lambda a, b: a - b,
                "*": lambda a, b: a * b,
                "/": lambda a, b: a / b,
                "//": lambda a, b: a // b,
                "%": lambda a, b: a % b,
                "**": lambda a, b: a**b,
                "==": lambda a, b: a == b,
                "!=": lambda a, b: a != b,
                "<": lambda a, b: a < b,
                ">": lambda a, b: a > b,
                "<=": lambda a, b: a <= b,
                ">=": lambda a, b: a >= b,
                "and": lambda a, b: a and b,
                "or": lambda a, b: a or b,
            }
            if op in operations:
                return operations[op](left_val, right_val)
        except (ZeroDivisionError, TypeError, ValueError) as e:
            logger.error(f"Error: {e}")
        return None

    def _execute_chained_compare(self, ir_node: Tuple) -> SymbolicValue:
        """Execute chained comparison"""
        if len(ir_node) >= 2:
            _, compare_parts = ir_node[:2]

            # ["chained_compare", [["<", left, right], ["<", right, another]]]
            if isinstance(compare_parts, (tuple, list)) and len(compare_parts) > 0:
                # Process comparison parts as a list of comparisons
                # We'll combine them with logical AND
                result = None
                all_conditions = []
                # Extract variable names for test inputs
                # variables = set()

                for compare_part in compare_parts:
                    if len(compare_part) >= 3:
                        op = compare_part[0]
                        left_ir = compare_part[1]
                        right_ir = compare_part[2]

                        left = self._execute_ir(left_ir)
                        right = self._execute_ir(right_ir)

                        # 创建可读条件用于跟踪，确保变量名正确
                        left_str = self._convert_expression_readable(left)
                        right_str = self._convert_expression_readable(right)

                        # 从原始IR中提取变量名，避免出现None
                        if (
                            left_str == "None"
                            and isinstance(left_ir, tuple)
                            and left_ir[0] == "name"
                        ):
                            left_str = left_ir[1]
                            # variables.add(left_ir[1])
                        if (
                            right_str == "None"
                            and isinstance(right_ir, tuple)
                            and right_ir[0] == "name"
                        ):
                            right_str = right_ir[1]
                            # variables.add(right_ir[1])

                        readable_condition = f"{left_str} {op} {right_str}"
                        all_conditions.append(readable_condition)

                        # Create expression value with the operator and operands
                        part_result = create_expression_value((op, left, right))

                        if result is None:
                            result = part_result
                        else:
                            # Combine with AND
                            result = create_expression_value(
                                ("and", result, part_result)
                            )

                # Add the combined condition to the result, but don't add to current path
                # 链式比较条件处理
                # 修复：返回组合后的条件，但不直接添加到路径
                # 避免与ConditionalHandler._execute_if_branch中的添加重复
                if self.current_path and all_conditions:
                    # 处理完成后重置标记
                    self._set_processing_chained_compare(False)

                return result if result is not None else create_concrete_value(True)
            # Original format handling
            elif len(ir_node) >= 4:
                _, left_ir, op, right_ir = ir_node[:4]
                left = self._execute_ir(left_ir)
                right = self._execute_ir(right_ir)
                return create_expression_value((op, left, right))

        return create_concrete_value(None)

    def _execute_comparison(self, ir_node: Tuple) -> SymbolicValue:
        """Execute comparison operations"""
        return self._execute_binary_op(ir_node)

    def _execute_match(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a match statement symbolically by exploring all possible paths"""
        if len(ir_node) < 3:
            return create_concrete_value(None)

        _, subject_ir, cases = ir_node
        subject_value = self._execute_ir(subject_ir)

        if not cases:
            return create_concrete_value(None)

        # Store current path to create branches from
        original_path = self.current_path
        new_paths = []

        # Collect all match values for wildcard constraint generation
        match_values = []
        wildcard_cases = []

        # First pass: collect match values and identify wildcard cases
        for i, case_ir in enumerate(cases):
            if not isinstance(case_ir, (tuple, list)) or len(case_ir) < 4:
                continue

            if case_ir[0] != "match_case":
                continue

            pattern = case_ir[1]
            if self._is_wildcard_pattern(pattern):
                wildcard_cases.append((i, case_ir))
            else:
                match_value = self._extract_match_value(pattern)
                if match_value is not None:
                    match_values.append(match_value)

        # Process each case to create separate execution paths
        for i, case_ir in enumerate(cases):
            if not isinstance(case_ir, (tuple, list)) or len(case_ir) < 4:
                continue

            if case_ir[0] != "match_case":
                continue

            pattern = case_ir[1]
            # guard = case_ir[2]  # TODO: Currently None in our test case
            body = case_ir[3]

            # Create a new path for this case
            case_path = self.path_manager.copy_path(original_path, f"match_case_{i}")

            # Add pattern matching condition to the path
            if self._is_wildcard_pattern(pattern):
                # For wildcard, add constraints that subject != all other match values
                subject_name = self._get_variable_name(subject_value)
                for value in match_values:
                    condition_expr = f"{subject_name} != {value}"
                    case_path.add_condition(PathCondition(condition_expr, True))
            else:
                condition_expr = self._create_match_condition(subject_value, pattern)
                if condition_expr:
                    case_path.add_condition(PathCondition(condition_expr, True))

            # Check if this path is satisfiable
            if case_path.is_satisfiable():
                # Set this as current path and execute the body
                self.current_path = case_path

                # Execute the case body
                if isinstance(body, (tuple, list)):
                    for stmt in body:
                        self._execute_ir(stmt)

                new_paths.append(case_path)

        # Add all new paths to the path manager
        for path in new_paths:
            self.path_manager.add_path(path)

        # Restore original path context
        self.current_path = original_path

        return create_concrete_value(None)

    def _execute_switch(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a switch statement symbolically by exploring all possible paths"""
        if len(ir_node) < 3:
            return create_concrete_value(None)

        _, subject_ir, cases = ir_node
        subject_value = self._execute_ir(subject_ir)

        if not cases:
            return create_concrete_value(None)

        # Store current path to create branches from
        original_path = self.current_path
        new_paths = []

        # Collect all case values for default constraint generation
        case_values = []
        for case_ir in cases:
            if (
                isinstance(case_ir, (tuple, list))
                and len(case_ir) >= 3
                and case_ir[0] == "case"
            ):
                case_value = self._resolve_case_value(case_ir[1])
                if case_value is not None:
                    case_values.append(case_value)

        # Process each case to create separate execution paths
        for i, case_ir in enumerate(cases):
            if not isinstance(case_ir, (tuple, list)) or len(case_ir) < 2:
                continue

            case_type = case_ir[0]
            if case_type == "case":
                if len(case_ir) < 3:
                    continue
                pattern = case_ir[1]
                body = case_ir[2]
                case_name = f"case_{i}"
            elif case_type == "default":
                if len(case_ir) < 2:
                    continue
                pattern = None  # default case matches everything
                body = case_ir[1]
                case_name = f"default_{i}"
            else:
                continue

            # Create a new path for this case
            case_path = self.path_manager.copy_path(original_path, case_name)

            # Add pattern matching condition to the path
            if case_type == "case" and pattern is not None:
                # Add equality condition for specific case
                condition_expr = self._create_switch_condition(subject_value, pattern)
                if condition_expr:
                    case_path.add_condition(PathCondition(condition_expr, True))
            elif case_type == "default":
                # Add negative conditions for default case (not equal to any specific case)
                subject_name = self._get_variable_name(subject_value)
                for case_value in case_values:
                    condition_expr = f"{subject_name} != {case_value}"
                    case_path.add_condition(PathCondition(condition_expr, True))

            # Check if this path is satisfiable
            if case_path.is_satisfiable():
                # Set this as current path and execute the body
                self.current_path = case_path

                # Execute the case body
                if isinstance(body, (tuple, list)):
                    for stmt in body:
                        self._execute_ir(stmt)

                new_paths.append(case_path)

        # Add all new paths to the path manager
        for path in new_paths:
            self.path_manager.add_path(path)

        # Restore original path context
        self.current_path = original_path

        return create_concrete_value(None)

    def _extract_case_value(self, pattern: Any) -> Any:
        """Extract the case value from a switch case pattern"""
        if isinstance(pattern, (tuple, list)) and len(pattern) >= 2:
            if pattern[0] == "const":
                return pattern[1]
            elif pattern[0] == "name":
                # Handle enum names and other named constants
                return pattern[1]
        return None

    def _resolve_case_value(self, pattern: Any) -> Any:
        """Resolve case value, including enum name resolution"""
        if isinstance(pattern, (tuple, list)) and len(pattern) >= 2:
            if pattern[0] == "const":
                return pattern[1]
            elif pattern[0] == "name":
                enum_name = pattern[1]
                # Check both current and global environments for enum constants
                if enum_name in self.current_env.variables:
                    enum_value = self.current_env.variables[enum_name]
                elif enum_name in self.global_env.variables:
                    enum_value = self.global_env.variables[enum_name]
                else:
                    return None

                # Extract the actual value
                if hasattr(enum_value, "value") and enum_value.value is not None:
                    return enum_value.value
                else:
                    return enum_value
        return None

    def _create_switch_condition(
        self, subject_value: SymbolicValue, pattern: Any
    ) -> str:
        """Create a condition string for switch case matching"""
        case_value = self._extract_case_value(pattern)
        if case_value is not None:
            subject_name = self._get_variable_name(subject_value)
            # Check if this is a pattern with name reference (like enum)
            if (
                isinstance(pattern, (tuple, list))
                and len(pattern) >= 2
                and pattern[0] == "name"
            ):
                # For enum names, try to resolve to actual value
                enum_name = case_value

                # Check both current and global environments for enum constants
                enum_value = None
                if enum_name in self.current_env.variables:
                    enum_value = self.current_env.variables[enum_name]
                elif enum_name in self.global_env.variables:
                    enum_value = self.global_env.variables[enum_name]

                if enum_value is not None:
                    # Get the actual enum value
                    if hasattr(enum_value, "value") and enum_value.value is not None:
                        formatted_value = str(enum_value.value)
                    else:
                        formatted_value = str(enum_value)
                else:
                    # Fallback to enum name if not found
                    formatted_value = enum_name
            elif isinstance(case_value, str):
                # For string literals, add quotes
                formatted_value = f'"{case_value}"'
            else:
                formatted_value = str(case_value)
            return f"{subject_name} == {formatted_value}"
        return ""

    def _is_wildcard_pattern(self, pattern: Tuple) -> bool:
        """Check if pattern is a wildcard pattern (_)"""
        if not isinstance(pattern, (tuple, list)) or len(pattern) < 2:
            return False

        return (
            pattern[0] == "match_as"
            and len(pattern) >= 3
            and pattern[1] is None
            and pattern[2] is None
        )

    def _extract_match_value(self, pattern: Tuple) -> Any:
        """Extract the match value from a pattern for constraint generation"""
        if not isinstance(pattern, (tuple, list)) or len(pattern) < 2:
            return None

        if pattern[0] == "match_value":
            value_ir = pattern[1]
            if isinstance(value_ir, (tuple, list)) and len(value_ir) >= 2:
                if value_ir[0] == "const":
                    return value_ir[1]

        return None

    def _create_match_condition(
        self, subject_value: SymbolicValue, pattern: Tuple
    ) -> str:
        """Create a condition string for pattern matching"""
        if not isinstance(pattern, (tuple, list)) or len(pattern) < 2:
            return ""

        pattern_type = pattern[0]

        if pattern_type == "match_value":
            # Extract the value to match against
            value_ir = pattern[1]
            if isinstance(value_ir, (tuple, list)) and len(value_ir) >= 2:
                if value_ir[0] == "const":
                    match_value = value_ir[1]
                    subject_name = self._get_variable_name(subject_value)
                    # Format the match value properly for string literals
                    if isinstance(match_value, str):
                        formatted_value = f'"{match_value}"'
                    else:
                        formatted_value = str(match_value)
                    return f"{subject_name} == {formatted_value}"

        return ""

    def _get_variable_name(self, symbolic_value: SymbolicValue) -> str:
        """Extract variable name from symbolic value for condition creation"""
        if symbolic_value.name:
            return symbolic_value.name
        elif symbolic_value.type == SymbolicValueType.SYMBOLIC:
            return str(symbolic_value)
        else:
            return str(symbolic_value)

    def _ir_to_readable_string(self, ir_node: Any) -> str:
        """Converts an IR node to a readable string for display."""
        if isinstance(ir_node, (list, tuple)):
            if not ir_node:
                return ""
            op = ir_node[0]
            if op == "name":
                return ir_node[1]
            if op == "const":
                return str(ir_node[1])
            if op == "assign":
                target = self._ir_to_readable_string(ir_node[1])
                value = self._ir_to_readable_string(ir_node[2])
                # Simplified, doesn't show type
                return f"{target} = {value}"
            if op in {"<", ">", "==", "!=", "<=", ">=", "+", "-", "*", "/"}:
                left = self._ir_to_readable_string(ir_node[1])
                right = self._ir_to_readable_string(ir_node[2])
                return f"{left} {op} {right}"
            if op in {"p++", "p--"}:
                var = self._ir_to_readable_string(ir_node[1])
                return f"{var}{op[1:]}"
            # For blocks like init
            if isinstance(op, (list, tuple)):
                return "; ".join([self._ir_to_readable_string(n) for n in ir_node])
        return str(ir_node)

    def _execute_c_for(self, ir_node: Tuple) -> SymbolicValue:
        """Execute a C-style for loop by transforming it to a while loop."""
        _, init, condition, update, body = ir_node

        # 1. Execute init
        if init:
            self._execute_ir(init)

        # 2. Create a new body for the while loop that includes the original body and the update
        new_body_stmts = list(body)
        if update:
            if isinstance(update, (list, tuple)) and update[0] == 'block':
                new_body_stmts.extend(update[1])
            else:
                new_body_stmts.append(update)

        new_body_block = ('block', tuple(new_body_stmts))

        # 3. Create a while loop IR node
        while_loop_ir = ("while", condition, new_body_block)

        # 4. Execute the while loop
        return self._execute_ir(while_loop_ir)

    def _execute_post_increment(self, ir_node: Tuple) -> SymbolicValue:
        """Execute post-increment operation (var++)"""
        _, var_expr = ir_node

        # Get current value
        current_value = self._execute_ir(var_expr)

        # Increment the variable
        if isinstance(var_expr, tuple) and len(var_expr) >= 2 and var_expr[0] == "name":
            var_name = var_expr[1]
            if var_name in self.current_env.variables:
                old_val = self.current_env.variables[var_name]
                if hasattr(old_val, "value") and isinstance(
                    old_val.value, (int, float)
                ):
                    new_val = create_concrete_value(old_val.value + 1)
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val
                else:
                    # Create symbolic increment
                    new_val = self.current_env.create_symbol(f"{var_name}_inc")
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val

        if self.current_path:
            var_str = self._ir_to_readable_string(var_expr)
            self.current_path.add_statement(f"{var_str}++")

        # Return the original value (post-increment semantics)
        return current_value

    def _execute_post_decrement(self, ir_node: Tuple) -> SymbolicValue:
        """Execute post-decrement operation (var--)"""
        _, var_expr = ir_node

        # Get current value
        current_value = self._execute_ir(var_expr)

        # Decrement the variable
        if isinstance(var_expr, tuple) and len(var_expr) >= 2 and var_expr[0] == "name":
            var_name = var_expr[1]
            if var_name in self.current_env.variables:
                old_val = self.current_env.variables[var_name]
                if hasattr(old_val, "value") and isinstance(
                    old_val.value, (int, float)
                ):
                    new_val = create_concrete_value(old_val.value - 1)
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val
                else:
                    # Create symbolic decrement
                    new_val = self.current_env.create_symbol(f"{var_name}_dec")
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val

        if self.current_path:
            var_str = self._ir_to_readable_string(var_expr)
            self.current_path.add_statement(f"{var_str}--")

        # Return the original value (post-decrement semantics)
        return current_value

    def _execute_pre_increment(self, ir_node: Tuple) -> SymbolicValue:
        """Execute pre-increment operation (++var)"""
        _, var_expr = ir_node

        # Increment the variable first
        if isinstance(var_expr, tuple) and len(var_expr) >= 2 and var_expr[0] == "name":
            var_name = var_expr[1]
            if var_name in self.current_env.variables:
                old_val = self.current_env.variables[var_name]
                if hasattr(old_val, "value") and isinstance(
                    old_val.value, (int, float)
                ):
                    new_val = create_concrete_value(old_val.value + 1)
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val
                else:
                    # Create symbolic increment
                    new_val = self.current_env.create_symbol(f"{var_name}_preinc")
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val
                return new_val

        if self.current_path:
            var_str = self._ir_to_readable_string(var_expr)
            self.current_path.add_statement(f"++{var_str}")

        return self._execute_ir(var_expr)

    def _execute_pre_decrement(self, ir_node: Tuple) -> SymbolicValue:
        """Execute pre-decrement operation (--var)"""
        _, var_expr = ir_node

        # Decrement the variable first
        if isinstance(var_expr, tuple) and len(var_expr) >= 2 and var_expr[0] == "name":
            var_name = var_expr[1]
            if var_name in self.current_env.variables:
                old_val = self.current_env.variables[var_name]
                if hasattr(old_val, "value") and isinstance(
                    old_val.value, (int, float)
                ):
                    new_val = create_concrete_value(old_val.value - 1)
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val
                else:
                    # Create symbolic decrement
                    new_val = self.current_env.create_symbol(f"{var_name}_predec")
                    self.current_env.variables[var_name] = new_val
                    if self.current_path:
                        self.current_path.variables[var_name] = new_val
                return new_val

        if self.current_path:
            var_str = self._ir_to_readable_string(var_expr)
            self.current_path.add_statement(f"--{var_str}")

        return self._execute_ir(var_expr)

    def _execute_aug_assign(self, ir_node: Tuple) -> SymbolicValue:
        """Execute augmented assignment (+=, -=, *=, etc.)"""
        _, target, op, value = ir_node

        # Get target variable name
        if isinstance(target, tuple) and len(target) >= 2 and target[0] == "name":
            var_name = target[1]
        else:
            var_name = str(target)

        # Execute the value expression
        value_result = self._execute_ir(value)

        # Get current variable value
        current_val = self.current_env.variables.get(var_name, create_concrete_value(0))

        # Perform the operation
        if op == "+=":
            if (
                hasattr(current_val, "value")
                and hasattr(value_result, "value")
                and isinstance(current_val.value, (int, float))
                and isinstance(value_result.value, (int, float))
            ):
                new_val = create_concrete_value(current_val.value + value_result.value)
            else:
                new_val = self.current_env.create_symbol(f"{var_name}_add")
        elif op == "-=":
            if (
                hasattr(current_val, "value")
                and hasattr(value_result, "value")
                and isinstance(current_val.value, (int, float))
                and isinstance(value_result.value, (int, float))
            ):
                new_val = create_concrete_value(current_val.value - value_result.value)
            else:
                new_val = self.current_env.create_symbol(f"{var_name}_sub")
        elif op == "*=":
            if (
                hasattr(current_val, "value")
                and hasattr(value_result, "value")
                and isinstance(current_val.value, (int, float))
                and isinstance(value_result.value, (int, float))
            ):
                new_val = create_concrete_value(current_val.value * value_result.value)
            else:
                new_val = self.current_env.create_symbol(f"{var_name}_mul")
        else:
            # Generic handling for other operators
            new_val = self.current_env.create_symbol(
                f"{var_name}_{op.replace('=', '')}"
            )

        # Update variable
        self.current_env.variables[var_name] = new_val
        if self.current_path:
            self.current_path.variables[var_name] = new_val

        if self.current_path:
            target_str = self._ir_to_readable_string(target)
            value_str = self._ir_to_readable_string(value)
            self.current_path.add_statement(f"{target_str} {op} {value_str}")

        return new_val

    def _execute_print(self, ir_node: Tuple) -> None:
        pass

    def _execute_binop(self, ir_node: Tuple) -> None:
        pass

    def _analyze_function_definition(
        self,
        func_name: str,
        params: List[str],
        body_ir: Any,
        param_types: List[Any],
        return_type: Any,
    ) -> List[ExecutionPath]:
        """Analyze all paths within a function definition"""
        # Save current state
        original_path_manager = self.path_manager
        original_current_path = self.current_path
        original_env = self.current_env

        # Reset for function analysis
        self.path_manager = PathManager()
        self.current_path = self.path_manager.create_path(f"func_{func_name}_")

        if isinstance(return_type, tuple):
            type1, type2 = return_type
            assert type1 == 'name'
            return_type = type2

        if return_type is None:
            self.current_path.return_type = None
        elif return_type in 'int enum'.split():
            self.current_path.return_type = 'int'
        elif return_type.startswith('struct_'):
            return_name = return_type[7:]
            # self.struct_types[name]
            assert return_name in self.struct_types, f"Struct type {return_name} not found"
            # print(self.struct_types[return_name])
            self.current_path.return_type = {
                'kind': "struct",
                'name': return_name,
                'fields': self.struct_types[return_name]
            }
            # raise
        else:
            raise ValueError(f"Return type {return_type} is not valid")

        # Create function environment with symbolic parameters
        func_env = SymbolicEnvironment(self.global_env)
        if not param_types:
            # TODO: it is old style
            for param in params:
                symbol = func_env.create_symbol(param)
                func_env.set_variable(param, symbol)
                self.current_path.variables[param] = symbol
        else:
            for param, param_type in zip(params, param_types):
                if param_type is None:
                    symbol = func_env.create_symbol(param)
                    func_env.set_variable(param, symbol)
                    self.current_path.variables[param] = symbol
                else:
                    # TODO: Handle param_type[1]
                    if isinstance(param_type, str):
                        if param_type in [
                            "enum",
                            "unsigned char",
                            "int",
                            "_Bool",
                            "unsigned short int",
                        ]:
                            symbol = func_env.create_symbol(param, "int")
                            func_env.set_variable(param, symbol)
                            self.current_path.variables[param] = symbol
                            self.current_path.variable_types[param] = "int"
                            if param_type == 'enum': # TODO: get real enum range
                                self.current_path.variable_raw_types[param] = "int"
                                self.current_path.add_condition(PathCondition(f"0 <= {param}", True))
                            elif param_type == 'int':
                                self.current_path.variable_raw_types[param] = "int"
                                self.current_path.add_condition(PathCondition(f"-2147483648 <= {param} <= 2147483647", True))
                            else:
                                self.current_path.variable_raw_types[param] = param_type
                            # TODO
                            if param_type == "unsigned char":
                                self.current_path.add_condition(PathCondition(f"0 <= {param} < 256", True))

                        else:
                            raise ValueError(
                                f"!!Invalid param_type: {param_type} {repr(param_type)} {type(param_type)} for {param}"
                            )
                    else:
                        symbol = func_env.create_symbol(param, param_type[1])
                        func_env.set_variable(param, symbol)
                        self.current_path.variables[param] = symbol
                        self.current_path.variable_types[param] = param_type[1]
                        self.current_path.variable_raw_types[param] = param_type[1]
                        # raise NotImplementedError(f"SymbolicExecutor: param_type[1] not implemented. {param_type}")

        self.current_env = func_env
        self._execute_function_body(body_ir)

        # 函数体执行完毕后，获取所有完整路径
        function_paths = self.path_manager.finalize_paths()

        # Restore original state
        self.path_manager = original_path_manager
        self.current_path = original_current_path
        self.current_env = original_env
        return function_paths

    def _execute_function_body(self, body_ir: Any) -> None:
        """Execute function body statements with proper path forking"""
        if isinstance(body_ir, (tuple, list)):
            # 使用递归方式处理语句，确保所有路径都被正确处理
            self._execute_statements_recursive(body_ir, 0)
        else:
            raise Exception("Function execution failed 2")

    def _execute_statements_recursive(self, statements, start_index):
        """递归执行语句，处理条件分支的路径分叉

        这个方法是符号执行的核心，负责：
        1. 检测 if 语句并创建分支路径
        2. 为每个分支递归执行剩余语句
        3. 正确处理 return 语句，避免继续执行后续语句

        重要：当路径遇到 return 语句时，该路径应该被标记为 COMPLETED，
        不再执行后续语句。这确保了条件分支中的 return 不会被覆盖。
        """
        if start_index >= len(statements):
            # 到达函数末尾，添加当前路径到路径管理器
            if self.current_path and self.current_path not in self.path_manager.paths:
                self.path_manager.add_path(self.current_path)
            return

        stmt = statements[start_index]
        if isinstance(stmt, str):  # Skip docstrings
            self._execute_statements_recursive(statements, start_index + 1)
            return

        # 检查是否是条件语句
        is_if_stmt = isinstance(stmt, tuple) and len(stmt) > 0 and stmt[0] == "if"
        is_match_stmt = isinstance(stmt, tuple) and len(stmt) > 0 and stmt[0] == "match"
        is_switch_stmt = (
            isinstance(stmt, tuple) and len(stmt) > 0 and stmt[0] == "switch"
        )
        is_while_stmt = isinstance(stmt, tuple) and len(stmt) > 0 and stmt[0] == "while"
        is_for_stmt = isinstance(stmt, tuple) and len(stmt) > 0 and stmt[0] == "for"
        is_c_for_stmt = isinstance(stmt, tuple) and len(stmt) > 0 and stmt[0] == "c_for"

        if is_if_stmt or is_match_stmt or is_switch_stmt or is_while_stmt or is_for_stmt or is_c_for_stmt:
            # 保存当前状态
            # original_path = self.current_path
            original_env = self.current_env.copy()

            # 执行条件语句（这会创建分支路径）
            self._execute_ir(stmt)

            # 获取所有当前路径管理器中的路径（包括新创建的分支）
            current_paths = self.path_manager.paths.copy()

            # 清空路径管理器，避免重复添加
            self.path_manager.paths.clear()

            # 为每个分支路径继续执行剩余语句
            for path in current_paths:
                # 设置当前路径
                self.current_path = path
                self.current_env = (
                    path.environment.copy()
                    if hasattr(path, "environment") and path.environment
                    else original_env.copy()
                )

                # 关键修复：如果路径已经完成（遇到return），则不继续执行后续语句
                if (
                    hasattr(path, "state")
                    and path.state == ExecutionPathState.COMPLETED
                ):
                    # 路径已完成，添加到路径管理器但不继续执行
                    if path not in self.path_manager.paths:
                        self.path_manager.add_path(path)
                    continue

                # 递归执行剩余语句
                self._execute_statements_recursive(statements, start_index + 1)
        elif is_match_stmt or is_switch_stmt:
            # 处理 match/switch 语句，类似于 if 语句的处理
            # 保存当前状态
            original_env = self.current_env.copy()

            # 执行 match/switch 语句（这会创建分支路径）
            self._execute_ir(stmt)

            # 获取所有当前路径管理器中的路径（包括新创建的分支）
            current_paths = self.path_manager.paths.copy()

            # 清空路径管理器，避免重复添加
            self.path_manager.paths.clear()

            # 为每个分支路径继续执行剩余语句
            for path in current_paths:
                # 设置当前路径
                self.current_path = path
                self.current_env = (
                    path.environment.copy()
                    if hasattr(path, "environment") and path.environment
                    else original_env.copy()
                )

                # 关键修复：如果路径已经完成（遇到return），则不继续执行后续语句
                if (
                    hasattr(path, "state")
                    and path.state == ExecutionPathState.COMPLETED
                ):
                    # 路径已完成，添加到路径管理器但不继续执行
                    if path not in self.path_manager.paths:
                        self.path_manager.add_path(path)
                    continue

                # 递归执行剩余语句
                self._execute_statements_recursive(statements, start_index + 1)
        else:
            # 非条件语句，正常执行
            self._execute_ir(stmt)
            if self.current_path is None:  # Return statement ended path
                # 如果路径被return语句终止，仍需要将其添加到路径管理器
                return

            # 继续执行剩余语句
            self._execute_statements_recursive(statements, start_index + 1)

    def _make_condition_readable(self, condition: Any) -> str:
        """Convert IR condition to readable format with recursive tuple handling"""
        # 处理IR节点的特殊情况 - 直接提取变量名
        if (
            isinstance(condition, tuple)
            and len(condition) >= 2
            and condition[0] == "name"
        ):
            var_name = condition[1]
            # Try to get the actual value from current path if available
            if self.current_path and var_name in self.current_path.variables:
                var_value = self.current_path.variables[var_name]
                return self._make_condition_readable(var_value)

            return var_name  # 直接返回变量名

        if condition is None:
            return "None"
        if hasattr(condition, "value") and hasattr(condition, "type"):
            if condition.type == SymbolicValueType.EXPRESSION:
                return self._make_condition_readable(condition.value)
            elif condition.type == SymbolicValueType.SYMBOLIC:
                # Try to get actual value from current path
                var_name = condition.name
                if (
                    self.current_path
                    and var_name
                    and var_name in self.current_path.variables
                ):
                    var_value = self.current_path.variables[var_name]
                    if var_value is not condition:
                        return self._make_condition_readable(var_value)

                return condition.name or str(condition.value)
            elif condition.type == SymbolicValueType.CONCRETE:
                return "None" if condition.value is None else str(condition.value)
            else:
                return str(condition)

        elif isinstance(condition, tuple) and len(condition) >= 3:
            op, left, right = condition[0], condition[1], condition[2]
            left_readable = self._make_condition_readable(left)
            right_readable = self._make_condition_readable(right)

            # 确保变量名不是 "None"
            if (
                left_readable == "None"
                and isinstance(left, tuple)
                and left[0] == "name"
            ):
                left_readable = left[1]
            if (
                right_readable == "None"
                and isinstance(right, tuple)
                and right[0] == "name"
            ):
                right_readable = right[1]

            # Add parentheses for and/or operators when operands are complex expressions
            if self._needs_parentheses_for_condition_precedence(left, op):
                left_readable = f"({left_readable})"

            # Check if right operand needs parentheses
            if self._needs_parentheses_for_condition_precedence(right, op):
                right_readable = f"({right_readable})"

            return f"{left_readable} {op} {right_readable}"

        try:
            return self._convert_expression_readable(condition)
        except (AttributeError, TypeError, ValueError) as e:
            # Expression conversion failed, use string representation
            logger.error(f"Error: {e}")
            if self.debug:
                logger.error(f"Debug: Condition readability conversion failed: {e}")
            return str(condition)

    def _simplify_display(self, value: Any) -> str:
        """Simplify value display for better readability"""
        if hasattr(value, "type") and hasattr(value, "value"):
            if hasattr(value, "original_ir") and value.original_ir:
                try:
                    return self._convert_value_display(value.original_ir)
                except (AttributeError, TypeError, ValueError) as e:
                    logger.error(f"Error: {e}")
                    # Original IR conversion failed, continue with other display options

            if value.type == SymbolicValueType.CONCRETE:
                return str(value.value)
            elif value.type == SymbolicValueType.SYMBOLIC:
                return getattr(value, "name", str(value.value)) or str(value.value)
            else:  # EXPRESSION
                return self._simplify_display(value.value)

        try:
            return self._convert_value_display(value)
        except (AttributeError, TypeError, ValueError) as e:
            logger.error(f"Error: {e}")
            # Value display conversion failed, use string representation
            if self.debug:
                logger.error(f"Debug: Value display conversion failed: {e}")
            return str(value)

    def _convert_value_display(self, value: Any) -> str:
        """Internal simplified value display converter"""
        if isinstance(value, str):
            return value
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, tuple):
            return self._convert_expression_readable(value)
        elif isinstance(value, list):
            items = [self._convert_value_display(item) for item in value]
            return f"[{', '.join(items)}]"
        return str(value)

    def _convert_expression_readable(self, expr: Any) -> str:
        """Internal simplified expression to readable format converter"""
        if expr is None:
            return "None"  # 明确处理 None 值
        if isinstance(expr, str):
            return expr
        elif isinstance(expr, (int, float, bool)):
            return str(expr)
        elif hasattr(expr, "type") and hasattr(expr, "value"):
            # 处理符号值
            if expr.type == SymbolicValueType.SYMBOLIC:
                return expr.name or str(expr.value)
            elif expr.type == SymbolicValueType.CONCRETE:
                return "None" if expr.value is None else str(expr.value)
            elif expr.type == SymbolicValueType.EXPRESSION:
                return self._convert_expression_readable(expr.value)
        elif isinstance(expr, tuple) and len(expr) >= 1:
            if len(expr) == 3 and isinstance(expr[0], str):
                op, left, right = expr
                left_str = self._convert_expression_readable(left)
                right_str = self._convert_expression_readable(right)

                # Add parentheses for and/or operators when operands are complex expressions
                if self._needs_parentheses_for_precedence(left, op):
                    left_str = f"({left_str})"

                # Check if right operand needs parentheses
                if self._needs_parentheses_for_precedence(right, op):
                    right_str = f"({right_str})"

                return f"{left_str} {op} {right_str}"
            elif len(expr) == 2 and isinstance(expr[0], str):
                op, operand = expr
                operand_str = self._convert_expression_readable(operand)
                if op == '-':
                    return f"-({operand_str})"
                return f"{op}({operand_str})"
        return str(expr)

    def _needs_parentheses_for_precedence(self, operand: Any, parent_op: str) -> bool:
        """Check if operand needs parentheses when used with parent operator"""
        # If operand is not a tuple expression, no parentheses needed
        if not isinstance(operand, tuple) or len(operand) < 3:
            return False

        # If operand has a symbolic value with expression type, check its value
        if hasattr(operand, "type") and hasattr(operand, "value"):
            if operand.type == SymbolicValueType.EXPRESSION:
                return self._needs_parentheses_for_precedence(operand.value, parent_op)
            return False

        # Check if operand is a binary operation
        if len(operand) == 3 and isinstance(operand[0], str):
            operand_op = operand[0]

            # Define operator precedence (higher number = higher precedence)
            precedence = {
                "or": 1,
                "and": 2,
                "not": 3,
                "==": 4,
                "!=": 4,
                "<": 4,
                "<=": 4,
                ">": 4,
                ">=": 4,
                "+": 5,
                "-": 5,
                "*": 6,
                "/": 6,
                "//": 6,
                "%": 6,
                "**": 7,
            }

            parent_prec = precedence.get(parent_op, 0)
            operand_prec = precedence.get(operand_op, 0)

            # Need parentheses if operand has lower precedence than parent
            # or if both are the same precedence and mixing and/or operators
            if operand_prec < parent_prec:
                return True
            elif (
                operand_prec == parent_prec
                and parent_op in ["and", "or"]
                and operand_op in ["and", "or"]
            ):
                # For same precedence and/or operators, add parentheses for clarity
                return parent_op != operand_op

        return False

    def _needs_parentheses_for_condition_precedence(
        self, operand: Any, parent_op: str
    ) -> bool:
        """Check if operand needs parentheses when used with parent operator in condition"""
        # If operand has a symbolic value with expression type, check its value
        if hasattr(operand, "type") and hasattr(operand, "value"):
            if operand.type == SymbolicValueType.EXPRESSION:
                return self._needs_parentheses_for_condition_precedence(
                    operand.value, parent_op
                )
            return False

        # If operand is not a tuple expression, no parentheses needed
        if not isinstance(operand, tuple) or len(operand) < 3:
            if self.debug:
                logger.debug(f"No parens needed - not tuple or too short: {operand}")
            return False

        # Check if operand is a binary operation - handle both raw tuples and SymbolicValue tuples
        operand_op = None
        if isinstance(operand[0], str):
            operand_op = operand[0]
        elif hasattr(operand[0], "type") and hasattr(operand[0], "value"):
            # This might be a SymbolicValue containing the operator
            if operand[0].type == SymbolicValueType.CONCRETE:
                operand_op = operand[0].value

        if operand_op and isinstance(operand_op, str):
            # Define operator precedence (higher number = higher precedence)
            precedence = {
                "or": 1,
                "and": 2,
                "not": 3,
                "==": 4,
                "!=": 4,
                "<": 4,
                "<=": 4,
                ">": 4,
                ">=": 4,
                "+": 5,
                "-": 5,
                "*": 6,
                "/": 6,
                "//": 6,
                "%": 6,
                "**": 7,
            }

            parent_prec = precedence.get(parent_op, 0)
            operand_prec = precedence.get(operand_op, 0)

            if self.debug:
                logger.debug(
                    f"Checking precedence: parent_op={parent_op} (prec={parent_prec}), operand_op={operand_op} (prec={operand_prec})"
                )

            # Need parentheses if operand has lower precedence than parent
            # or if both are the same precedence and mixing and/or operators
            if operand_prec < parent_prec:
                if self.debug:
                    logger.debug(
                        f"Adding parens - lower precedence: {operand_op} < {parent_op}"
                    )
                return True
            elif (
                operand_prec == parent_prec
                and parent_op in ["and", "or"]
                and operand_op in ["and", "or"]
            ):
                # For same precedence and/or operators, add parentheses for clarity
                result = parent_op != operand_op
                if self.debug:
                    logger.debug(f"Same precedence and/or - adding parens: {result}")
                return result

        if self.debug:
            logger.debug(f"No parens needed for: {operand} with parent {parent_op}")
        return False

    def _handle_non_tuple_node(self, ir_node: Any) -> SymbolicValue:
        """Handle non-tuple IR nodes"""
        if isinstance(ir_node, str):
            # Distinguish between variable references and string literals
            # String literals are typically:
            # 1. Single uppercase letters (grades: A, B, C, D, F)
            # 2. Capitalized words (Low, High, Medium)
            # 3. Common string values that are not typical variable names

            # Check if it's likely a string literal rather than a variable
            # TODO: better handling of string literals
            if (
                (len(ir_node) == 1 and ir_node.isupper())
                or ir_node.istitle()
                or not ir_node.isidentifier()
                or ir_node in {"True", "False", "None"}
            ):
                # Treat as string literal
                return create_concrete_value(ir_node)
            else:
                # Treat as variable reference
                return self.current_env.get_variable(ir_node)

        if isinstance(ir_node, int):
            # ir_node is int
            return create_concrete_value(ir_node)

        # For any other type, just create a concrete value with the original object
        logger.warning(
            f"Handling unexpected non-tuple node type: {type(ir_node).__name__}"
        )
        try:
            return create_concrete_value(ir_node)
        except Exception as e:
            logger.error(
                f"Error creating concrete value for {type(ir_node).__name__}: {e}"
            )
            return create_symbolic_value(f"unknown_{type(ir_node).__name__}")
