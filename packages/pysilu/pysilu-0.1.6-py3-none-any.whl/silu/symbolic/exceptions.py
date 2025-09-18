#!/usr/bin/env python3
"""
Custom exceptions for the symbolic execution engine.

This module defines specific exception types for better error handling
and debugging in the symbolic execution process.
"""

from typing import Optional, Any


class SymbolicExecutionError(Exception):
    """Base exception for symbolic execution errors"""

    def __init__(self, message: str, context: Optional[dict] = None):
        super().__init__(message)
        self.context = context or {}


class PathLimitExceededError(SymbolicExecutionError):
    """Raised when the maximum number of execution paths is exceeded"""

    def __init__(
        self, current_paths: int, max_paths: int, context: Optional[dict] = None
    ):
        message = f"Path limit exceeded: {current_paths} >= {max_paths}"
        super().__init__(message, context)
        self.current_paths = current_paths
        self.max_paths = max_paths


class LoopIterationLimitError(SymbolicExecutionError):
    """Raised when loop iteration limit is exceeded"""

    def __init__(
        self,
        loop_id: str,
        iterations: int,
        max_iterations: int,
        context: Optional[dict] = None,
    ):
        message = f"Loop iteration limit exceeded for {loop_id}: {iterations} >= {max_iterations}"
        super().__init__(message, context)
        self.loop_id = loop_id
        self.iterations = iterations
        self.max_iterations = max_iterations


class SymbolicValueError(SymbolicExecutionError):
    """Raised when there's an error with symbolic value operations"""

    def __init__(
        self, operation: str, value: Any, reason: str, context: Optional[dict] = None
    ):
        message = f"Symbolic value error in {operation}: {reason} (value: {value})"
        super().__init__(message, context)
        self.operation = operation
        self.value = value
        self.reason = reason


class Z3ConstraintError(SymbolicExecutionError):
    """Raised when there's an error with Z3 constraint generation or solving"""

    def __init__(
        self,
        constraint_type: str,
        expression: str,
        reason: str,
        context: Optional[dict] = None,
    ):
        message = f"Z3 constraint error ({constraint_type}): {reason} for expression: {expression}"
        super().__init__(message, context)
        self.constraint_type = constraint_type
        self.expression = expression
        self.reason = reason


class UnsupportedIRNodeError(SymbolicExecutionError):
    """Raised when an unsupported IR node type is encountered"""

    def __init__(self, node_type: str, node_data: Any, context: Optional[dict] = None):
        message = f"Unsupported IR node type: {node_type} (data: {node_data})"
        super().__init__(message, context)
        self.node_type = node_type
        self.node_data = node_data


class EnvironmentError(SymbolicExecutionError):
    """Raised when there's an error with the symbolic environment"""

    def __init__(
        self,
        operation: str,
        variable_name: str,
        reason: str,
        context: Optional[dict] = None,
    ):
        message = (
            f"Environment error in {operation} for variable '{variable_name}': {reason}"
        )
        super().__init__(message, context)
        self.operation = operation
        self.variable_name = variable_name
        self.reason = reason


class FunctionAnalysisError(SymbolicExecutionError):
    """Raised when there's an error during function analysis"""

    def __init__(self, function_name: str, reason: str, context: Optional[dict] = None):
        message = f"Function analysis error for '{function_name}': {reason}"
        super().__init__(message, context)
        self.function_name = function_name
        self.reason = reason


class PathSatisfiabilityError(SymbolicExecutionError):
    """Raised when path satisfiability check fails"""

    def __init__(self, path_id: str, reason: str, context: Optional[dict] = None):
        message = f"Path satisfiability error for path '{path_id}': {reason}"
        super().__init__(message, context)
        self.path_id = path_id
        self.reason = reason


class IRParsingError(SymbolicExecutionError):
    """Raised when there's an error parsing IR from file or string"""

    def __init__(
        self,
        source_type: str,
        source_info: str,
        reason: str,
        context: Optional[dict] = None,
    ):
        message = f"IR parsing error from {source_type} '{source_info}': {reason}"
        super().__init__(message, context)
        self.source_type = source_type
        self.source_info = source_info
        self.reason = reason


class ConfigurationError(SymbolicExecutionError):
    """Raised when there's an error with symbolic executor configuration"""

    def __init__(
        self, parameter: str, value: Any, reason: str, context: Optional[dict] = None
    ):
        message = f"Configuration error for parameter '{parameter}' with value {value}: {reason}"
        super().__init__(message, context)
        self.parameter = parameter
        self.value = value
        self.reason = reason


def create_execution_context(
    current_path: Optional[Any] = None,
    current_env: Optional[Any] = None,
    ir_node: Optional[Any] = None,
) -> dict:
    """
    Create a context dictionary for exception reporting.

    Args:
        current_path: Current execution path
        current_env: Current symbolic environment
        ir_node: Current IR node being processed

    Returns:
        Dictionary with context information
    """
    context = {}

    if current_path:
        context["path_id"] = getattr(current_path, "path_id", "unknown")
        context["path_conditions"] = len(getattr(current_path, "conditions", []))
        context["path_statements"] = len(getattr(current_path, "statements", []))

    if current_env:
        context["environment_vars"] = len(getattr(current_env, "variables", {}))
        context["environment_functions"] = len(getattr(current_env, "functions", {}))

    if ir_node:
        if isinstance(ir_node, (tuple, list)) and len(ir_node) > 0:
            context["ir_node_type"] = ir_node[0]
            context["ir_node_length"] = len(ir_node)
        else:
            context["ir_node_type"] = type(ir_node).__name__

    return context
