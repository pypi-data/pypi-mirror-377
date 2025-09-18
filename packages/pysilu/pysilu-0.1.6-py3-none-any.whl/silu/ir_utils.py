#!/usr/bin/env python3
"""
IR Utilities Module

This module provides shared utility functions for IR processing across different
components (interpreter, symbolic executor, IR-to-source converter, LLVM converter).

Contains common functionality for:
- IR parsing from JSON and files
- IR format validation
- JSON to tuple conversion
- File I/O operations
- Error handling utilities
"""

import json
import ast
from typing import Any, Union, Tuple, List, Dict, Optional
from pathlib import Path


class IRParseError(Exception):
    """Exception raised when IR parsing fails."""

    pass


class IRValidationError(Exception):
    """Exception raised when IR validation fails."""

    pass


# ============ JSON and Format Conversion ============


def json_to_tuples(obj: Any) -> Any:
    """
    Recursively convert JSON lists to tuples for IR processing.

    This is needed because IR nodes are expected to be tuples, but JSON
    only supports lists. This function preserves the nested structure
    while converting all lists to tuples.

    Args:
        obj: JSON object (can be list, dict, or primitive)

    Returns:
        Object with all lists converted to tuples
    """
    if isinstance(obj, list):
        return tuple(json_to_tuples(item) for item in obj)
    elif isinstance(obj, dict):
        return {key: json_to_tuples(value) for key, value in obj.items()}
    else:
        return obj


def tuples_to_json_compatible(obj: Any) -> Any:
    """
    Convert tuples back to lists for JSON serialization.

    Args:
        obj: Object that may contain tuples

    Returns:
        Object with all tuples converted to lists
    """
    if isinstance(obj, tuple):
        return [tuples_to_json_compatible(item) for item in obj]
    elif isinstance(obj, list):
        return [tuples_to_json_compatible(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: tuples_to_json_compatible(value) for key, value in obj.items()}
    else:
        return obj


# ============ IR Parsing Functions ============


def parse_ir_from_json_string(json_string: str) -> Union[Tuple, List]:
    """
    Parse IR from a JSON string.

    Handles both pure JSON format and Python literal format with
    null/true/false replacements.

    Args:
        json_string: JSON string containing IR data

    Returns:
        Parsed IR as tuple structure

    Raises:
        IRParseError: If parsing fails
    """
    if not json_string or not json_string.strip():
        raise IRParseError("Empty or whitespace-only input")

    json_string = json_string.strip()

    # Try JSON parsing first
    try:
        ir_data = json.loads(json_string)
        return json_to_tuples(ir_data)
    except json.JSONDecodeError:
        pass

    # Fall back to Python literal evaluation with replacements
    try:
        # Replace JSON null/boolean literals with Python equivalents
        python_string = json_string.replace("null", "None")
        python_string = python_string.replace("true", "True")
        python_string = python_string.replace("false", "False")

        # Use ast.literal_eval for safety
        ir_data = ast.literal_eval(python_string)
        return ir_data
    except (ValueError, SyntaxError) as e:
        raise IRParseError(f"Failed to parse IR string: {e}")


def parse_ir_from_file(
    file_path: Union[str, Path], encoding: str = "utf-8"
) -> Union[Tuple, List]:
    """
    Parse IR from a file.

    Args:
        file_path: Path to the IR file
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed IR as tuple structure

    Raises:
        IRParseError: If file reading or parsing fails
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"IR file not found: {file_path}")

    if not file_path.is_file():
        raise IRParseError(f"Path is not a file: {file_path}")

    try:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()

        return parse_ir_from_json_string(content)

    except UnicodeDecodeError as e:
        raise IRParseError(
            f"Failed to decode file {file_path} with encoding {encoding}: {e}"
        )
    except IOError as e:
        raise IRParseError(f"Failed to read file {file_path}: {e}")


# ============ IR Validation Functions ============


def validate_ir_node_format(ir_node: Any) -> bool:
    """
    Validate basic IR node format.

    A valid IR node should be a tuple/list with at least one element,
    where the first element is a string (the opcode).

    Args:
        ir_node: IR node to validate

    Returns:
        True if format is valid, False otherwise
    """
    if not isinstance(ir_node, (tuple, list)):
        return False

    if len(ir_node) == 0:
        return False

    if not isinstance(ir_node[0], str):
        return False

    return True


def validate_ir_program(ir_program: Any) -> bool:
    """
    Validate IR program format.

    A valid IR program should be a module node.

    Args:
        ir_program: IR program to validate

    Returns:
        True if format is valid, False otherwise
    """
    if not validate_ir_node_format(ir_program):
        return False

    if ir_program[0] != "module":
        return False

    if len(ir_program) < 2:
        return False

    return True


def validate_ir_node_structure(
    ir_node: Any,
    expected_opcode: str = None,
    min_args: int = None,
    max_args: int = None,
) -> bool:
    """
    Validate specific IR node structure.

    Args:
        ir_node: IR node to validate
        expected_opcode: Expected opcode (optional)
        min_args: Minimum number of arguments (excluding opcode)
        max_args: Maximum number of arguments (excluding opcode)

    Returns:
        True if structure is valid, False otherwise
    """
    if not validate_ir_node_format(ir_node):
        return False

    opcode = ir_node[0]
    args = ir_node[1:]

    if expected_opcode is not None and opcode != expected_opcode:
        return False

    if min_args is not None and len(args) < min_args:
        return False

    if max_args is not None and len(args) > max_args:
        return False

    return True


# ============ IR Analysis Utilities ============


def extract_ir_opcodes(ir_node: Any, visited: Optional[set] = None) -> set:
    """
    Extract all opcodes used in an IR tree.

    Args:
        ir_node: Root IR node
        visited: Set to track visited nodes (for cycle detection)

    Returns:
        Set of all opcodes found in the IR tree
    """
    if visited is None:
        visited = set()

    opcodes = set()

    # Avoid infinite recursion
    node_id = id(ir_node)
    if node_id in visited:
        return opcodes
    visited.add(node_id)

    if isinstance(ir_node, (tuple, list)):
        if len(ir_node) > 0 and isinstance(ir_node[0], str):
            # This is an IR node with opcode
            opcodes.add(ir_node[0])

        # Recursively process all child nodes
        for child in ir_node:
            if child != ir_node[0] or not isinstance(ir_node[0], str):
                opcodes.update(extract_ir_opcodes(child, visited))

    return opcodes


def count_ir_nodes(ir_node: Any, visited: Optional[set] = None) -> int:
    """
    Count the total number of IR nodes in a tree.

    Args:
        ir_node: Root IR node
        visited: Set to track visited nodes (for cycle detection)

    Returns:
        Total number of IR nodes
    """
    if visited is None:
        visited = set()

    # Avoid infinite recursion
    node_id = id(ir_node)
    if node_id in visited:
        return 0
    visited.add(node_id)

    if not isinstance(ir_node, (tuple, list)):
        return 0

    count = 0

    # Count this node if it's a valid IR node (starts with string opcode)
    if len(ir_node) > 0 and isinstance(ir_node[0], str):
        count = 1

    # Recursively count child nodes
    for child in ir_node:
        if child != ir_node[0] or not isinstance(ir_node[0], str):
            count += count_ir_nodes(child, visited)

    return count


def find_ir_nodes_by_opcode(
    ir_node: Any, target_opcode: str, visited: Optional[set] = None
) -> List[Any]:
    """
    Find all IR nodes with a specific opcode.

    Args:
        ir_node: Root IR node
        target_opcode: Opcode to search for
        visited: Set to track visited nodes (for cycle detection)

    Returns:
        List of all nodes with the target opcode
    """
    if visited is None:
        visited = set()

    results = []

    # Avoid infinite recursion
    node_id = id(ir_node)
    if node_id in visited:
        return results
    visited.add(node_id)

    if isinstance(ir_node, (tuple, list)):
        if (
            len(ir_node) > 0
            and isinstance(ir_node[0], str)
            and ir_node[0] == target_opcode
        ):
            results.append(ir_node)

        # Recursively search all child nodes
        for child in ir_node:
            if child != ir_node[0] or not isinstance(ir_node[0], str):
                results.extend(find_ir_nodes_by_opcode(child, target_opcode, visited))

    return results


# ============ File I/O Utilities ============


def save_ir_to_file(
    ir_data: Any,
    file_path: Union[str, Path],
    format: str = "json",
    encoding: str = "utf-8",
    indent: int = 2,
) -> None:
    """
    Save IR data to a file.

    Args:
        ir_data: IR data to save
        file_path: Output file path
        format: Output format ("json" or "python")
        encoding: File encoding
        indent: Indentation level for pretty printing

    Raises:
        IRValidationError: If format is unsupported
        IOError: If file writing fails
    """
    file_path = Path(file_path)

    if format == "json":
        # Convert tuples to lists for JSON compatibility
        json_compatible_data = tuples_to_json_compatible(ir_data)
        content = json.dumps(json_compatible_data, indent=indent)
    elif format == "python":
        # Use repr for Python literal format
        content = repr(ir_data)
    else:
        raise IRValidationError(f"Unsupported output format: {format}")

    try:
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Failed to write IR to file {file_path}: {e}")


# ============ Error Handling Utilities ============


def safe_ir_parse(content: str, context: str = "IR parsing") -> Optional[Any]:
    """
    Safely parse IR content with error logging.

    Args:
        content: IR content to parse
        context: Context description for error messages

    Returns:
        Parsed IR data or None if parsing fails
    """
    try:
        return parse_ir_from_json_string(content)
    except IRParseError as e:
        print(f"Warning: {context} failed: {e}")
        return None


def get_ir_node_info(ir_node: Any) -> Dict[str, Any]:
    """
    Get diagnostic information about an IR node.

    Args:
        ir_node: IR node to analyze

    Returns:
        Dictionary with diagnostic information
    """
    info = {
        "type": type(ir_node).__name__,
        "is_valid_format": validate_ir_node_format(ir_node),
        "length": len(ir_node) if isinstance(ir_node, (tuple, list)) else 0,
        "opcode": None,
        "args_count": 0,
    }

    if isinstance(ir_node, (tuple, list)) and len(ir_node) > 0:
        info["opcode"] = (
            ir_node[0] if isinstance(ir_node[0], str) else type(ir_node[0]).__name__
        )
        info["args_count"] = len(ir_node) - 1

    return info


# ============ Configuration and Constants ============


class IRConfig:
    """Configuration constants for IR processing."""

    # Default file encoding
    DEFAULT_ENCODING = "utf-8"

    # Supported IR opcodes (can be extended by modules)
    CORE_OPCODES = {
        "module",
        "const",
        "const_b",
        "name",
        "assign",
        "call",
        "if",
        "while",
        "for",
        "func_def",
        "return",
        "break",
        "continue",
        "binary_op",
        "unary_op",
        "chained_compare",
        "list",
        "tuple",
        "dict",
        "attribute",
        "subscript",
        "match",
        "match_case",
        "typedef",
        "typedef_struct",
        "typedef_enum",
        "tuple_assign",
        "subscript_assign",
        "aug_assign",
    }

    # File size limits (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # Recursion limits
    MAX_RECURSION_DEPTH = 1000


def check_file_size(file_path: Union[str, Path]) -> bool:
    """
    Check if file size is within limits.

    Args:
        file_path: Path to check

    Returns:
        True if file size is acceptable, False otherwise
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return False

    file_size = file_path.stat().st_size
    return file_size <= IRConfig.MAX_FILE_SIZE
