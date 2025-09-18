from enum import Enum
from loguru import logger
import sys
from copy import deepcopy
from typing import Any, Dict, Optional, Tuple, Union
from abc import ABC, abstractmethod

from z3.z3 import Option

from .symbolic.condition_utils import PathCondition

from .symbolic.builtin_utils import (
    SymbolicValue,
    create_symbolic_value,
    create_expression_value,  # TODO
)

from .symbolic.z3_utils import (
    Z3_AVAILABLE,
)

from .symbolic.builtin_utils import (
    SymbolicValueType,
    create_concrete_value,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from silu.symbolic_executor import SymbolicExecutor

logger.remove()  # 移除默认的 handler
logger.add(
    sink=sys.stderr,  # 或 sys.stdout
    level="DEBUG",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{file.path}</cyan>:<cyan>{line}</cyan>:<cyan>{function}</cyan>: - "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# 可用等级： "TRACE" < "DEBUG" < "INFO" < "SUCCESS" < "WARNING" < "ERROR" < "CRITICAL"

# Configuration Constants

class Config:
    """Configuration constants for symbolic execution"""

    DEFAULT_MAX_PATHS = 100
    DEFAULT_MAX_LOOP_ITERATIONS = 5
    PERFORMANCE_MAX_PATHS = 50
    PERFORMANCE_MAX_LOOP_ITERATIONS = 3
    DEFAULT_PATH_PREFIX = "path_"
    DEFAULT_ENCODING = "utf-8"

class ExecutionPathState(Enum):
    """Enumeration of execution path states"""

    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    UNSATISFIABLE = "unsatisfiable"

class SymbolicEnvironment:
    """Environment for symbolic execution with improved encapsulation"""

    def __init__(self, parent: Optional["SymbolicEnvironment"] = None):
        self.parent = parent
        self.variables: Dict[str, SymbolicValue] = {}
        self.variable_types: Dict[str, str] = {}
        self.return_type: Optional[str] = None
        self.functions: Dict[str, Any] = {}
        self.symbol_counter = 0
        self.z3_variables: Dict[str, Any] = {}

    def create_symbol(
        self, name: Optional[str] = None, var_type: str = "int"
    ) -> SymbolicValue:
        """Create a new symbolic value with optional Z3 variable"""
        if not name:
            name = f"sym_{self.symbol_counter}"
            self.symbol_counter += 1

        # Create Z3 variable if available
        if Z3_AVAILABLE and name not in self.z3_variables:
            self.z3_variables[name] = self._create_z3_variable(name, var_type)

        return create_symbolic_value(name)

    def _create_z3_variable(self, name: str, var_type: str) -> Any:
        """Create Z3 variable based on type"""
        from .symbolic.z3_utils import create_z3_variable

        return create_z3_variable(name, var_type)

    def has_variable(self, name: str) -> bool:
        """Check if a variable exists in the current or parent scope"""
        if name in self.variables:
            return True
        elif self.parent:
            return self.parent.has_variable(name)
        return False

    def get_variable(self, name: str) -> SymbolicValue:
        """Get a variable value with proper scoping"""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            # Create a symbolic variable for undefined variables
            symbol = self.create_symbol(name)
            self.variables[name] = symbol
            return symbol

    def set_variable(self, name: str, value: SymbolicValue) -> None:
        """Set a variable value, respecting scope."""
        env = self
        while env:
            if name in env.variables:
                env.variables[name] = value
                return
            env = env.parent
        # If not found, set in current env
        self.variables[name] = value

    def set_variable_type(self, name: str, var_type: str) -> None:
        """Set a variable value"""
        self.variable_types[name] = var_type

    def copy(self) -> "SymbolicEnvironment":
        """Create a deep copy of the environment"""
        new_env = SymbolicEnvironment(self.parent)
        new_env.variables = deepcopy(self.variables)
        new_env.variable_types = deepcopy(self.variable_types)
        new_env.return_type = deepcopy(self.return_type)
        new_env.functions = deepcopy(self.functions)
        new_env.symbol_counter = self.symbol_counter
        new_env.z3_variables = self.z3_variables.copy()
        return new_env

class IRNodeHandler(ABC):
    """Abstract base class for IR node handlers"""

    @abstractmethod
    def can_handle(self, ir_node: Tuple) -> bool:
        """Check if this handler can process the given IR node"""
        pass

    @abstractmethod
    def handle(self, ir_node: Tuple, executor: "SymbolicExecutor") -> SymbolicValue:
        """Handle the IR node and return its symbolic value"""
        pass

class AssignmentHandler(IRNodeHandler):
    """Handler for assignment operations"""

    def can_handle(self, ir_node: Tuple) -> bool:
        return (
            isinstance(ir_node, tuple) and len(ir_node) > 0 and ir_node[0] == "assign"
        )

    def handle(self, ir_node: Tuple, executor: "SymbolicExecutor") -> SymbolicValue:
        try:
            from .symbolic.builtin_utils import (
                create_concrete_value,
                create_symbolic_value,
            )

            _, var_name_ir, value_ir, var_type = ir_node

            # Extract actual variable name from IR node
            if (
                isinstance(var_name_ir, (tuple, list))
                and len(var_name_ir) >= 2
                and var_name_ir[0] == "name"
            ):
                var_name = var_name_ir[1]
            else:
                var_name = var_name_ir

            # Handle struct instance creation
            if isinstance(var_type, str) and var_type.startswith("struct_"):
                struct_name = var_type[7:]  # Remove 'struct_' prefix
                if (
                    hasattr(executor, "struct_types")
                    and struct_name in executor.struct_types
                ):
                    # Create a symbolic value for the struct instance
                    value = create_concrete_value(var_type)
                else:
                    # Unknown struct type, create a symbolic value
                    value = create_symbolic_value(f"new_{var_type}")
            else:
                # Normal assignment
                value = (
                    executor._execute_ir(value_ir)
                    if value_ir is not None
                    else create_concrete_value(None)
                )

            executor.current_env.set_variable(var_name, value)
            if var_type is not None and not isinstance(
                var_type, str
            ):  # ('name', 'int')
                executor.current_env.set_variable_type(var_name, var_type[1])

            if executor.current_path:
                simplified_value = executor._simplify_display(value)
                executor.current_path.add_statement(f"{var_name} = {simplified_value}")
                executor.current_path.variables[var_name] = value
                if var_type is not None and not isinstance(var_type, str):
                    executor.current_path.variable_types[var_name] = var_type[1]

            return value
        except Exception as e:
            logger.error(f"Error: {e}")
            if executor.current_path:
                executor.current_path.add_statement(f"Error in assignment: {e}")
                executor.current_path.state = ExecutionPathState.ERROR
            return create_concrete_value(None)

class ConditionalHandler(IRNodeHandler):
    """Handler for if/elif/else statements"""

    def can_handle(self, ir_node: Tuple) -> bool:
        return isinstance(ir_node, tuple) and len(ir_node) > 0 and ir_node[0] == "if"

    def handle(self, ir_node: Tuple, executor: "SymbolicExecutor") -> SymbolicValue:
        if len(ir_node) == 4:
            _, condition_ir, then_block, else_block = ir_node
        else:
            _, condition_ir, then_block = ir_node
            else_block = None

        # 执行条件求值
        condition = executor._execute_ir(condition_ir)

        readable_condition = executor._make_condition_readable(condition)

        # Handle concrete conditions directly
        if condition.type == SymbolicValueType.CONCRETE:
            return self._execute_concrete_if(
                executor, condition, readable_condition, then_block, else_block
            )

        # Check path limits
        if len(executor.path_manager.paths) >= executor.path_manager.max_paths:
            if executor.current_path:
                executor.current_path.add_statement(
                    f"Path limit reached at if condition: {readable_condition}"
                )
            return create_concrete_value(None)

        # Execute symbolic if with path splitting
        return self._execute_symbolic_if(
            executor, condition, readable_condition, then_block, else_block
        )

    def _execute_concrete_if(
        self, executor, condition, readable_condition, then_block, else_block
    ):
        """Execute if statement with concrete condition"""
        if executor.current_path:
            executor.current_path.add_statement(f"if {readable_condition}:")

        if condition.value:
            if then_block:
                executor._execute_ir(then_block)
        else:
            logger.error("condition is False. It is dead code?")
            if else_block:
                executor._execute_ir(else_block)
        return create_concrete_value(None)

    def _execute_symbolic_if(
        self, executor, condition, readable_condition, then_block, else_block
    ):
        """Execute if statement with symbolic condition by splitting paths"""
        original_path = executor.current_path
        original_env = executor.current_env.copy()

        # TODO: Generate Z3 constraint
        # logger.debug(f"Gen Z3 constraint for condition: {condition} readable: {readable_condition}")
        # z3_constraint = executor._generate_z3_constraint(condition)
        z3_constraint = None
        # logger.debug(f"Generated Z3 constraint: {z3_constraint}")

        # Store all paths that are created from this if statement
        created_paths = []

        # Save the original path and environment before any execution
        original_current_path = executor.current_path
        original_current_env = original_env.copy()

        # Execute true path with a fresh copy of the original path and environment
        true_paths = self._execute_if_branch(
            executor,
            original_path,
            original_env.copy(),
            condition,
            readable_condition,
            True,
            then_block,
            z3_constraint,
            "if",
        )
        if true_paths:
            created_paths.extend(true_paths)

        # Reset to original state before executing the false path
        executor.current_path = original_current_path
        executor.current_env = original_current_env.copy()

        # Execute false path with a fresh environment
        false_paths = self._execute_if_branch(
            executor,
            original_path,
            original_env.copy(),
            condition,
            readable_condition,
            False,
            else_block,
            z3_constraint,
            "else",
        )
        if false_paths:
            created_paths.extend(false_paths)

        # Don't reset current_path to None - this breaks nested if statements
        # Instead, continue with one of the created paths for further execution
        if created_paths:
            # 将所有创建的路径添加到路径管理器，供递归执行使用
            for path in created_paths:
                if path not in executor.path_manager.paths:
                    executor.path_manager.add_path(path)
            # 仍然保持一个当前路径以继续执行
            executor.current_path = created_paths[0]
        else:
            # If no paths created, restore the original path
            executor.current_path = original_current_path
            executor.current_env = original_current_env.copy()

        return create_concrete_value(None)

    def _execute_if_branch(
        self,
        executor,
        original_path,
        original_env,
        condition,
        readable_condition,
        is_true_branch,
        block,
        z3_constraint,
        branch_name,
    ):
        """Execute a single branch of an if statement"""
        # or ExecutionPath("temp")
        branch_path = executor.path_manager.copy_path(original_path)

        # Add condition
        condition_obj = PathCondition(
            readable_condition,
            is_true_branch,
            raw_expression=condition,
            z3_constraint=z3_constraint,
        )
        branch_path.add_condition(condition_obj)

        statement = (
            f"{branch_name} {readable_condition}:"
            if is_true_branch
            else f"else not {readable_condition}:"
        )
        branch_path.add_statement(statement)

        # Execute block with proper path context
        executor.current_path = branch_path
        executor.current_env = original_env.copy()

        # Store the current path count before executing the block
        # initial_path_count = len(executor.path_manager.paths)

        if block:
            # try:
            # Handle block execution - if block is a list/tuple of statements, execute each one
            if isinstance(block, (list, tuple)):
                for stmt in block:
                    executor._execute_ir(stmt)
            else:
                executor._execute_ir(block)
            # except Exception:
            #     exc_type, exc_value, exc_tb = sys.exc_info()
            #     error_msg = str(exc_value)
            #     # error_msg = str(e)
            #     logger.error(f"Error: {error_msg}")
            #     if executor.current_path:
            #         executor.current_path.add_statement(
            #             f"Error in {branch_name} block: {error_msg}"
            #         )
            #         executor.current_path.state = ExecutionPathState.ERROR

        # Always add the current path to the path manager if it's satisfiable
        # This ensures that leaf paths (those without further nested conditions) are captured
        #
        # logger.info(f"Adding path to path manager: {executor.current_path}")
        if executor.current_path:
            pass
            # TODO
            # executor.current_path.satisfiable = executor.current_path.is_satisfiable()

            # logger.info(f"path conds: {executor.current_path.satisfiable}")
            # logger.info(f"path satisfiable: {executor.current_path.satisfiable}")
            # logger.info(f"path test_inputs: {executor.current_path.test_inputs}")

            # 不需要在这里添加路径到路径管理器
            # 这将由递归执行逻辑处理

            # 返回当前路径作为列表，与修改后的 _execute_symbolic_if 接口保持一致
            return [executor.current_path] if executor.current_path else []

class LoopHandler(IRNodeHandler):
    """Handler for loop operations"""

    def can_handle(self, ir_node: Tuple) -> bool:
        return (
            isinstance(ir_node, tuple)
            and len(ir_node) > 0
            and ir_node[0] in ["while", "for"]
        )

    def handle(self, ir_node: Tuple, executor: "SymbolicExecutor") -> SymbolicValue:
        if ir_node[0] == "while":
            return self._handle_while_loop(ir_node, executor)
        elif ir_node[0] == "for":
            return self._handle_for_loop(ir_node, executor)
        return create_concrete_value(None)

    def _handle_while_loop(
        self, ir_node: Tuple, executor: "SymbolicExecutor"
    ) -> SymbolicValue:
        """Handle while loop with enhanced constraint analysis"""
        _, condition_ir, body_ir = ir_node
        condition = executor._execute_ir(condition_ir)
        readable_condition = executor._make_condition_readable(condition)

        if executor.current_path:
            executor.current_path.add_statement(f"while {readable_condition}:")

        # For concrete false conditions, skip the loop entirely
        if condition.type == SymbolicValueType.CONCRETE and not condition.value:
            if executor.current_path:
                executor.current_path.add_statement(
                    "# Loop not entered (condition false)"
                )
            return create_concrete_value(None)

        return self._execute_while_iterations(
            executor, ir_node, condition, readable_condition, body_ir
        )

    def _execute_while_iterations(
        self, executor, ir_node, condition, readable_condition, body_ir
    ):
        """Execute while loop by creating a path for exit and a path for iterations."""
        original_path = executor.current_path

        # Path where loop condition is false
        exit_path = executor.path_manager.copy_path(original_path, "while_exit")
        exit_cond = PathCondition(readable_condition, False, raw_expression=condition)
        exit_path.add_condition(exit_cond)
        if exit_path.is_satisfiable():
            executor.path_manager.add_path(exit_path)

        # Path where loop condition is true
        entry_path = executor.path_manager.copy_path(original_path, "while_entry")
        entry_cond = PathCondition(readable_condition, True, raw_expression=condition)
        entry_path.add_condition(entry_cond)

        if entry_path.is_satisfiable():
            # Unroll the loop for a few iterations on this path
            executor.current_path = entry_path
            for i in range(executor.max_loop_iterations):
                executor._execute_ir(body_ir)
                if executor.current_path.state == ExecutionPathState.COMPLETED:
                    break

            # After unrolling, this path is considered to have exited the loop.
            # We add the exit condition again.
            cond_after_loop = executor._execute_ir(ir_node[1])
            readable_cond_after = executor._make_condition_readable(cond_after_loop)
            exit_cond_after = PathCondition(readable_cond_after, False, raw_expression=cond_after_loop)
            entry_path.add_condition(exit_cond_after)

            if entry_path.is_satisfiable():
                executor.path_manager.add_path(entry_path)

        executor.current_path = None
        return create_concrete_value(None)

    def _handle_for_loop(
        self, ir_node: Tuple, executor: "SymbolicExecutor"
    ) -> SymbolicValue:
        """Handle for loop with enhanced range analysis"""
        if len(ir_node) < 4:
            return create_concrete_value(None)

        _, var_name_ir, iter_expr, body_ir = ir_node[:4]

        if isinstance(var_name_ir, tuple) and var_name_ir[0] == 'name':
            var_name = var_name_ir[1]
        else:
            var_name = str(var_name_ir)

        if executor.current_path:
            executor.current_path.add_statement(f"for {var_name} in ...:") # Simplified iter_expr

        # Check if it's a range call
        if executor.loop_analyzer._is_range_expression(iter_expr):
            bounds = executor.loop_analyzer.extract_range_bounds(iter_expr)
            if bounds:
                return self._execute_range_loop(
                    executor, var_name, bounds, body_ir, ir_node
                )

        # Fallback to simple iteration
        return self._execute_generic_for(executor, var_name, iter_expr, body_ir)

    def _execute_range_loop(self, executor, var_name, bounds, body_ir, loop_node):
        """Execute range-based for loop"""
        original_path = executor.current_path
        original_env = executor.current_env.copy()

        stop_val_ir = bounds.stop

        # Handle symbolic stop value
        if stop_val_ir[0] == 'name':
            stop_val_symbol = executor._execute_ir(stop_val_ir)
            stop_val_name = stop_val_symbol.name

            # Path 1: Loop does not execute at all (stop_val <= 0)
            no_loop_path = executor.path_manager.copy_path(original_path, "loop_skip")
            condition_str = f"{stop_val_name} <= 0"
            no_loop_path.add_condition(PathCondition(condition_str, True))
            no_loop_path.add_statement(f"# Loop not entered: {condition_str}")
            if no_loop_path.is_satisfiable():
                executor.path_manager.add_path(no_loop_path)

            # Paths 2 to max_loop_iterations + 1: Loop executes 1 to max_loop_iterations times
            for i in range(1, executor.max_loop_iterations + 1):
                iter_path = executor.path_manager.copy_path(original_path, f"loop_{i}_times")

                if i < executor.max_loop_iterations:
                    condition_str = f"{stop_val_name} == {i}"
                else: # Last path handles all larger values
                    condition_str = f"{stop_val_name} >= {i}"

                iter_path.add_condition(PathCondition(condition_str, True))
                iter_path.add_statement(f"# Loop executes {i} time(s): {condition_str}")

                if iter_path.is_satisfiable():
                    executor.current_path = iter_path
                    executor.current_env = original_env.copy()

                    # Simulate loop execution for 'i' iterations
                    for k in range(i):
                        loop_var = create_concrete_value(k)
                        loop_var.name = var_name
                        executor.current_env.set_variable(var_name, loop_var)
                        executor.current_path.variables[var_name] = loop_var

                        try:
                            self._execute_loop_body(executor, body_ir)
                        except Exception as e:
                            logger.error(f"Error in loop body execution: {e}")
                            if executor.current_path:
                                executor.current_path.add_statement(f"Error in loop body: {e}")
                                executor.current_path.state = ExecutionPathState.ERROR
                            break

                    if executor.current_path.state != ExecutionPathState.ERROR:
                        executor.path_manager.add_path(executor.current_path)

            executor.current_path = None
            return create_concrete_value(None)

        # Handle concrete stop value
        else:
            start_val = self._extract_literal(bounds.start)
            stop_val = self._extract_literal(bounds.stop)
            step_val = self._extract_literal(bounds.step)

            if not all(isinstance(x, int) for x in [start_val, stop_val, step_val]):
                 return create_concrete_value(None)

            loop_path = executor.path_manager.copy_path(original_path)
            executor.current_path = loop_path

            last_k = None
            for k in range(start_val, stop_val, step_val):
                last_k = k
                loop_var = create_concrete_value(k)
                loop_var.name = var_name
                executor.current_env.set_variable(var_name, loop_var)
                executor.current_path.variables[var_name] = loop_var

                try:
                    self._execute_loop_body(executor, body_ir)
                except Exception as e:
                    logger.error(f"Error in loop body execution: {e}")
                    if executor.current_path:
                        executor.current_path.add_statement(f"Error in loop body: {e}")
                        executor.current_path.state = ExecutionPathState.ERROR
                    break

            if last_k is not None:
                 loop_var = create_concrete_value(last_k)
                 loop_var.name = var_name
                 executor.current_path.variables[var_name] = loop_var
            elif start_val is not None:
                 loop_var = create_concrete_value(start_val)
                 loop_var.name = var_name
                 executor.current_path.variables[var_name] = loop_var

            if executor.current_path.state != ExecutionPathState.ERROR:
                executor.path_manager.add_path(executor.current_path)

            executor.current_path = None
            return create_concrete_value(None)

    def _extract_literal(self, expr) -> Union[int, Any]:
        """Extract literal value from expression"""
        if isinstance(expr, int):
            return expr
        if isinstance(expr, (tuple, list)) and len(expr) >= 2:
            if expr[0] == "literal" or expr[0] == "const":
                return expr[1]
        return expr

    def _is_valid_iteration(self, k: int, start: Any, stop: Any, step: Any) -> bool:
        """Check if iteration k is valid for the given range"""
        if not all(isinstance(x, int) for x in [start, stop, step]):
            return k < 3  # Fallback for symbolic values

        current_val = start + k * step
        return (step > 0 and current_val < stop) or (step < 0 and current_val > stop)

    def _execute_loop_body(self, executor, body_ir):
        """Execute loop body statements"""
        if isinstance(body_ir, (tuple, list)) and len(body_ir) > 0:
            if isinstance(body_ir[0], str):  # Single statement
                executor._execute_ir(body_ir)
            else:  # Multiple statements
                for stmt in body_ir:
                    executor._execute_ir(stmt)
        else:
            executor._execute_ir(body_ir)

    def _execute_generic_for(self, executor, var_name, iter_expr, body_ir):
        """Execute generic for loop (fallback)"""
        loop_var = executor.current_env.create_symbol(f"{var_name}_iter")
        executor.current_env.set_variable(var_name, loop_var)

        if executor.current_path:
            executor.current_path.add_statement(
                f"# Generic for loop: {var_name} = {loop_var}"
            )

        self._execute_loop_body(executor, body_ir)
        return create_concrete_value(None)

    def _handle_c_for_loop(self, executor, condition, update, body, loop_node):
        """Handle C-style for loop with enhanced analysis"""
        max_iterations = getattr(executor, "max_loop_iterations", 10)
        iterations = 0
        loop_id = f"c_for_{id(loop_node)}"

        try:
            while iterations < max_iterations:
                # Check loop condition
                if condition:
                    cond_result = executor._execute_ir(condition)
                    if hasattr(cond_result, "value") and not cond_result.value:
                        break

                    # TODO: Generate Z3 constraints for condition if available
                    # if executor.z3_available:
                    #     try:
                    #         z3_cond = executor._generate_z3_constraint(condition)
                    #         if z3_cond is not None:
                    #             executor.current_constraints.append(z3_cond)
                    #     except Exception as e:
                    #         raise
                    # Continue without Z3 constraint

                # Execute loop body
                executor._execute_ir(body)

                # Execute update statement
                if update:
                    executor._execute_ir(update)

                iterations += 1

                # Track iterations in path
                if executor.current_path:
                    executor.current_path.loop_iterations[loop_id] = iterations

        except Exception as e:
            logger.error(f"Error: {e}")
            if executor.current_path:
                executor.current_path.add_statement(f"Loop error: {str(e)}")

        # Record final iteration count
        if executor.current_path:
            executor.current_path.loop_iterations[loop_id] = iterations

        return create_concrete_value(None)
