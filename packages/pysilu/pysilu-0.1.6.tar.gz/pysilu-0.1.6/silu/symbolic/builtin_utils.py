#!/usr/bin/env python3
"""
Builtin Function Utilities for Symbolic Execution

This module provides utilities for handling builtin functions in symbolic execution,
including type conversions and other standard Python builtins.
"""

from typing import Any, Optional
from enum import Enum


class SymbolicValueType(Enum):
    """Types of symbolic values"""

    SYMBOLIC = "symbolic"
    CONCRETE = "concrete"
    EXPRESSION = "expression"


class SymbolicValue:
    """Represents a symbolic value that can be either concrete or an expression"""

    def __init__(
        self, value_type: SymbolicValueType, value: Any, name: Optional[str] = None
    ):
        self.type = value_type
        self.value = value
        self.name = name
        self.constraints = []
        self.original_ir = None

    def __str__(self) -> str:
        if self.type == SymbolicValueType.CONCRETE:
            if isinstance(self.value, str):
                return f'"{self.value}"'
            return str(self.value)
        elif self.type == SymbolicValueType.SYMBOLIC:
            return self.name or f"sym_{id(self)}"
        else:  # EXPRESSION
            return str(self.value)

    def __repr__(self) -> str:
        return f"SymbolicValue({self.type.name}, {self.value!r}, {self.name})"


def create_concrete_value(value: Any) -> SymbolicValue:
    """Create a concrete symbolic value"""
    return SymbolicValue(SymbolicValueType.CONCRETE, value)


def create_symbolic_value(name: str) -> SymbolicValue:
    """Create a symbolic value"""
    return SymbolicValue(SymbolicValueType.SYMBOLIC, None, name)


def create_expression_value(expression) -> SymbolicValue:
    """Create an expression symbolic value"""
    return SymbolicValue(SymbolicValueType.EXPRESSION, expression)


def symbolic_type_conversion(
    func_name: str, value: SymbolicValue, converter_func
) -> SymbolicValue:
    """
    Generic type conversion handler for symbolic values.

    Args:
        func_name: Name of the conversion function (e.g., 'int', 'float')
        value: The symbolic value to convert
        converter_func: Python function to apply for concrete values

    Returns:
        Converted symbolic value
    """
    if value.type == SymbolicValueType.CONCRETE:
        try:
            converted = converter_func(value.value)
            return create_concrete_value(converted)
        except (ValueError, TypeError, OverflowError, AttributeError):
            return create_expression_value(f"{func_name}({value})")
    else:
        return create_expression_value(f"{func_name}({value})")


def symbolic_int(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of int conversion"""
    return symbolic_type_conversion("int", value, int)


def symbolic_float(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of float conversion"""
    return symbolic_type_conversion("float", value, float)


def symbolic_str(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of str conversion"""
    return symbolic_type_conversion("str", value, str)


def symbolic_bool(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of bool conversion"""
    return symbolic_type_conversion("bool", value, bool)


def symbolic_type(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of type function"""
    return create_expression_value(f"type({value})")


def symbolic_isinstance(value: SymbolicValue, type_obj: SymbolicValue) -> SymbolicValue:
    """Symbolic version of isinstance function"""
    return create_expression_value(f"isinstance({value}, {type_obj})")


def symbolic_len(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of len function"""
    if value.type == SymbolicValueType.CONCRETE:
        try:
            # Try to get length for concrete values
            if hasattr(value.value, "__len__"):
                length = len(value.value)
                return create_concrete_value(length)
        except (TypeError, AttributeError, OverflowError):
            pass
    return create_expression_value(f"len({value})")


def symbolic_print(
    *args, current_path=None, simplify_display_func=None
) -> SymbolicValue:
    """
    Symbolic version of print function

    Args:
        *args: Arguments to print
        current_path: Current execution path (optional)
        simplify_display_func: Function to simplify argument display (optional)

    Returns:
        Symbolic value representing None (print returns None)
    """
    if current_path:
        if simplify_display_func:
            args_display = simplify_display_func(args)
        else:
            args_display = simplify_args_display(args)
        current_path.add_statement(f"print({args_display})")

    return create_concrete_value(None)


def symbolic_abs(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of abs function"""
    return symbolic_type_conversion("abs", value, abs)


def symbolic_max(*args) -> SymbolicValue:
    """Symbolic version of max function"""
    if (
        len(args) == 1
        and hasattr(args[0], "__iter__")
        and not isinstance(args[0], (str, bytes, bytearray))
    ):
        # max(iterable)
        iterable = args[0]
        if hasattr(iterable, "type") and iterable.type == SymbolicValueType.CONCRETE:
            try:
                result = max(iterable.value)
                return create_concrete_value(result)
            except (ValueError, TypeError, OverflowError):
                pass
        return create_expression_value(f"max({iterable})")
    else:
        # max(a, b, c, ...)
        args_str = ", ".join(str(arg) for arg in args)

        # Try to evaluate if all arguments are concrete
        if all(
            hasattr(arg, "type") and arg.type == SymbolicValueType.CONCRETE
            for arg in args
        ):
            try:
                values = [arg.value for arg in args]
                result = max(values)
                return create_concrete_value(result)
            except (ValueError, TypeError, OverflowError):
                pass

        return create_expression_value(f"max({args_str})")


def symbolic_min(*args) -> SymbolicValue:
    """Symbolic version of min function"""
    if (
        len(args) == 1
        and hasattr(args[0], "__iter__")
        and not isinstance(args[0], (str, bytes, bytearray))
    ):
        # min(iterable)
        iterable = args[0]
        if hasattr(iterable, "type") and iterable.type == SymbolicValueType.CONCRETE:
            try:
                result = min(iterable.value)
                return create_concrete_value(result)
            except (ValueError, TypeError, OverflowError):
                pass
        return create_expression_value(f"min({iterable})")
    else:
        # min(a, b, c, ...)
        args_str = ", ".join(str(arg) for arg in args)

        # Try to evaluate if all arguments are concrete
        if all(
            hasattr(arg, "type") and arg.type == SymbolicValueType.CONCRETE
            for arg in args
        ):
            try:
                values = [arg.value for arg in args]
                result = min(values)
                return create_concrete_value(result)
            except (ValueError, TypeError, OverflowError):
                pass

        return create_expression_value(f"min({args_str})")


def symbolic_range(*args) -> SymbolicValue:
    """Symbolic version of range function"""
    args_str = ", ".join(str(arg) for arg in args)

    # Try to create concrete range if all arguments are concrete integers
    if all(
        hasattr(arg, "type")
        and arg.type == SymbolicValueType.CONCRETE
        and isinstance(arg.value, int)
        for arg in args
    ):
        try:
            values = [arg.value for arg in args]
            # Keep as range object to preserve lazy evaluation semantics
            result = range(*values)
            return create_concrete_value(result)
        except (ValueError, TypeError, OverflowError):
            pass

    return create_expression_value(f"range({args_str})")

def symbolic_sqrt(value: SymbolicValue) -> SymbolicValue:
    """Symbolic version of sqrt function"""
    if value.type == SymbolicValueType.CONCRETE:
        try:
            import math
            converted = math.sqrt(value.value)
            return create_concrete_value(converted)
        except (ValueError, TypeError, OverflowError, AttributeError):
            return create_expression_value(f"sqrt({value})")
    else:
        return create_expression_value(f"sqrt({value})")


def simplify_args_display(args) -> str:
    """
    Simplify arguments display for better readability

    Args:
        args: Tuple/list of arguments

    Returns:
        Simplified string representation of arguments
    """
    simplified_args = []
    for arg in args:
        if (
            hasattr(arg, "value")
            and hasattr(arg, "type")
            and arg.type == SymbolicValueType.CONCRETE
        ):
            simplified_args.append(str(arg.value))
        else:
            simplified_args.append(str(arg))
    return ", ".join(simplified_args)


def create_builtin_functions_dict(current_path=None):
    """
    Create a dictionary of symbolic builtin functions

    Args:
        current_path: Current execution path (for print function)

    Returns:
        Dictionary mapping function names to symbolic implementations
    """
    return {
        "int": symbolic_int,
        "float": symbolic_float,
        "str": symbolic_str,
        "bool": symbolic_bool,
        "type": symbolic_type,
        "isinstance": symbolic_isinstance,
        "len": symbolic_len,
        "abs": symbolic_abs,
        "max": symbolic_max,
        "min": symbolic_min,
        "range": symbolic_range,
        "sqrt": symbolic_sqrt,
        "print": lambda *args: symbolic_print(
            *args,
            current_path=current_path,
            simplify_display_func=simplify_args_display,
        ),
    }


def is_builtin_function(name: str) -> bool:
    """Check if a name refers to a builtin function we handle"""
    builtins = {
        "int",
        "float",
        "str",
        "bool",
        "type",
        "isinstance",
        "len",
        "abs",
        "max",
        "min",
        "range",
        "sqrt",
        "print",
    }
    return name in builtins


def get_builtin_function(name: str, current_path=None):
    """
    Get a symbolic implementation of a builtin function

    Args:
        name: Name of the builtin function
        current_path: Current execution path (optional)

    Returns:
        Symbolic function implementation or None if not found
    """
    builtins_dict = create_builtin_functions_dict(current_path)
    return builtins_dict.get(name)
