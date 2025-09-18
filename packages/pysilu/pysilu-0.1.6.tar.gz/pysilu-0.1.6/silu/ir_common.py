#!/usr/bin/env python3
"""
IR Common Module

This module provides common utility functions for IR processing across different
components (interpreter, symbolic executor, IR-to-source converter, LLVM converter).

Unlike the ir_utils.py module which focuses on general IR parsing and validation,
this module provides functions specifically for IR node processing logic.
"""

import sys
from typing import Any, Dict, Callable, List, Optional
from . import ir_utils


class IRProcessingError(Exception):
    """Exception raised during IR node processing."""

    pass


# ============ IR Node Dispatching ============


def dispatch_ir_node(
    node: Any,
    handlers: Dict[str, Callable],
    default_handler: Optional[Callable] = None,
    debug: bool = False,
) -> Any:
    """
    Dispatch an IR node to the appropriate handler function.

    Args:
        node: IR node to dispatch
        handlers: Dictionary mapping opcodes to handler functions
        default_handler: Function to call if no handler is found
        debug: Whether to print debug information

    Returns:
        Result of processing the node

    Raises:
        IRProcessingError: If node is invalid or has no handler
    """
    if not ir_utils.validate_ir_node_format(node):
        raise IRProcessingError(f"Invalid IR node format: {node}")

    opcode = node[0]

    if debug:
        print(f"Dispatching node: {opcode}", file=sys.stderr)

    handler = handlers.get(opcode)

    if handler:
        return handler(node)
    elif default_handler:
        return default_handler(node)
    else:
        raise IRProcessingError(f"No handler for IR opcode: {opcode}")


def create_handlers_map(
    processor_obj: Any, prefix: str = "_process_"
) -> Dict[str, Callable]:
    """
    Create a handlers map from methods of a processor object.

    Args:
        processor_obj: Object with handler methods
        prefix: Prefix for handler method names

    Returns:
        Dictionary mapping opcodes to handler methods
    """
    handlers = {}

    for attr_name in dir(processor_obj):
        if attr_name.startswith(prefix):
            opcode = attr_name[len(prefix) :]
            handler = getattr(processor_obj, attr_name)
            if callable(handler):
                handlers[opcode] = handler

    return handlers


# ============ Debug and Logging ============


def log_ir_processing(
    opcode: str,
    args: List[Any],
    level: str = "INFO",
    extra_info: Optional[Dict] = None,
    output_stream=None,
) -> None:
    """
    Log information about IR node processing.

    Args:
        opcode: Node opcode
        args: Node arguments
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        extra_info: Additional information to log
        output_stream: Stream to write log to. Defaults to sys.stderr.
    """
    if output_stream is None:
        output_stream = sys.stderr

    if extra_info is None:
        extra_info = {}

    arg_summary = []
    for arg in args:
        if isinstance(arg, (list, tuple)) and len(arg) > 3:
            arg_summary.append(f"{type(arg).__name__}[{len(arg)} items]")
        elif isinstance(arg, (dict)) and len(arg) > 3:
            arg_summary.append(f"dict[{len(arg)} items]")
        else:
            arg_summary.append(repr(arg))

    log_message = f"[{level}] Processing {opcode}: {', '.join(arg_summary[:3])}"

    if extra_info:
        log_message += f" | {extra_info}"

    print(log_message, file=output_stream)


# ============ Error Handling ============


def handle_node_error(
    node: Any, error: Exception, context: str = "", raise_error: bool = True
) -> Optional[str]:
    """
    Handle an error that occurred during node processing.

    Args:
        node: IR node that caused the error
        error: Exception that was raised
        context: Additional context information
        raise_error: Whether to re-raise the error

    Returns:
        Error message if raise_error is False

    Raises:
        IRProcessingError: If raise_error is True
    """
    opcode = node[0] if ir_utils.validate_ir_node_format(node) else "unknown"

    error_message = f"Error processing {opcode} node: {error}"
    if context:
        error_message += f" (context: {context})"

    if raise_error:
        raise IRProcessingError(error_message) from error
    else:
        return error_message


# ============ Node Validation ============


def validate_node_args(
    node: Any,
    expected_opcode: str,
    min_args: Optional[int] = None,
    max_args: Optional[int] = None,
) -> None:
    """
    Validate an IR node's structure and arguments.

    Args:
        node: IR node to validate
        expected_opcode: Expected opcode for the node
        min_args: Minimum number of arguments (excluding opcode)
        max_args: Maximum number of arguments (excluding opcode)

    Raises:
        IRProcessingError: If validation fails
    """
    if not ir_utils.validate_ir_node_format(node):
        raise IRProcessingError(f"Invalid IR node format: {node}")

    opcode = node[0]
    args = node[1:]

    if opcode != expected_opcode:
        raise IRProcessingError(f"Expected opcode {expected_opcode}, got {opcode}")

    if min_args is not None and len(args) < min_args:
        raise IRProcessingError(
            f"{opcode} node requires at least {min_args} arguments, got {len(args)}"
        )

    if max_args is not None and len(args) > max_args:
        raise IRProcessingError(
            f"{opcode} node cannot have more than {max_args} arguments, got {len(args)}"
        )


# ============ Common Node Processing ============


def process_ir_block(
    statements: List[Any],
    process_func: Callable[[Any], Any],
    break_on_return: bool = False,
) -> List[Any]:
    """
    Process a block of IR statements.

    Args:
        statements: List of IR statements to process
        process_func: Function to process each statement
        break_on_return: Whether to stop processing after a return statement

    Returns:
        List of results from processing each statement
    """
    results = []

    for stmt in statements:
        result = process_func(stmt)
        results.append(result)

        # Check if this is a return statement and we should break
        if break_on_return and isinstance(stmt, (list, tuple)) and stmt[0] == "return":
            break

    return results


def extract_names_from_params(params: List[str]) -> List[str]:
    """
    Extract parameter names from a function definition's parameters.

    This handles both simple names and tuple unpacking patterns.

    Args:
        params: Parameter list from function definition

    Returns:
        List of parameter names
    """
    names = []

    for param in params:
        if isinstance(param, str):
            names.append(param)
        elif isinstance(param, (list, tuple)) and param[0] == "tuple_unpack":
            # Handle tuple unpacking parameters
            names.extend(param[1])
        else:
            raise IRProcessingError(f"Unsupported parameter format: {param}")

    return names


def process_const_node(node: Any) -> Any:
    """
    Process a constant node and extract its value.

    Args:
        node: Constant IR node

    Returns:
        Constant value

    Raises:
        IRProcessingError: If node is invalid
    """
    validate_node_args(node, "const", 1, 1)
    return node[1]


def is_valid_identifier(name: str) -> bool:
    """
    Check if a string is a valid Python identifier.

    Args:
        name: String to check

    Returns:
        True if name is a valid identifier, False otherwise
    """
    if not name:
        return False

    # First character must be alphabetic or underscore
    if not (name[0].isalpha() or name[0] == "_"):
        return False

    # Remaining characters must be alphanumeric or underscore
    for char in name[1:]:
        if not (char.isalnum() or char == "_"):
            return False

    # Check if it's a Python keyword
    import keyword

    if keyword.iskeyword(name):
        return False

    return True
