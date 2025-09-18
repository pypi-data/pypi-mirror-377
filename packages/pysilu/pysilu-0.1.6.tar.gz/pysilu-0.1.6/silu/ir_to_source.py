"""
Silu IR to Source Converter Module

This module provides functionality to convert Silu IR (Intermediate Representation)
back to readable source code. It can be used both as a standalone converter and
by other modules like the symbolic executor for displaying readable expressions.
"""

from typing import Any, Tuple
from .ir_utils import parse_ir_from_file, parse_ir_from_json_string, IRParseError


class IRToSourceConverter:
    """Converts IR tuples back to readable Silu/Python source code."""

    def __init__(self, indent_size: int = 4):
        self.indent_size = indent_size

    def convert_to_source(self, ir_node: Any, indent_level: int = 0) -> str:
        """Convert an IR node to source code string."""
        if isinstance(ir_node, tuple) and len(ir_node) >= 1:
            node_type = ir_node[0]

            # Handle different IR node types
            if node_type == "name":
                return self._convert_name(ir_node)
            elif node_type == "const":
                return self._convert_const(ir_node)
            elif node_type == "const_b":
                return self._convert_const_b(ir_node)
            elif node_type == "module":
                return self._convert_module(ir_node, indent_level)
            elif node_type == "assign":
                return self._convert_assign(ir_node, indent_level)
            elif node_type == "subscript_assign":
                return self._convert_subscript_assign(ir_node, indent_level)
            elif node_type == "aug_assign":
                return self._convert_aug_assign(ir_node, indent_level)
            elif node_type == "tuple_assign":
                return self._convert_tuple_assign(ir_node, indent_level)
            elif node_type == "multi_assign":
                return self._convert_multi_assign(ir_node, indent_level)
            elif node_type == "if":
                return self._convert_if(ir_node, indent_level)
            elif node_type == "while":
                return self._convert_while(ir_node, indent_level)
            elif node_type == "for":
                return self._convert_for(ir_node, indent_level)
            elif node_type == "func_def":
                return self._convert_func_def(ir_node, indent_level)
            elif node_type == "c_for":
                return self._convert_c_for(ir_node, indent_level)
            elif node_type == "aug_assign":
                return self._convert_aug_assign(ir_node, indent_level)
            elif node_type in ["p++", "p--", "++", "--"]:
                return self._convert_increment_decrement(ir_node, indent_level)
            elif node_type == "return":
                return self._convert_return(ir_node, indent_level)
            elif node_type == "call":
                return self._convert_call(ir_node, indent_level)
            elif node_type == "lambda":
                return self._convert_lambda(ir_node)
            elif node_type == "if_expr":
                return self._convert_if_expr(ir_node)
            elif node_type == "list":
                return self._convert_list(ir_node)
            elif node_type == "tuple":
                return self._convert_tuple(ir_node)
            elif node_type == "dict":
                return self._convert_dict(ir_node)
            elif node_type == "set":
                return self._convert_set(ir_node)
            elif node_type == "attribute":
                return self._convert_attribute(ir_node)
            elif node_type == "subscript":
                return self._convert_subscript(ir_node)
            elif node_type == "slice":
                return self._convert_slice(ir_node)
            elif node_type == "chained_compare":
                return self._convert_chained_compare(ir_node)
            elif node_type == "pass":
                return self._get_indent(indent_level) + "pass"
            elif node_type == "break":
                return self._get_indent(indent_level) + "break"
            elif node_type == "continue":
                return self._get_indent(indent_level) + "continue"
            elif node_type in ["==", "!=", "<", ">", "<=", ">="]:
                return self._convert_comparison(ir_node)
            elif node_type in ["and", "or"]:
                return self._convert_bool_op(ir_node)
            elif node_type == "not":
                return self._convert_unary_op(ir_node)
            elif node_type in ["+", "-", "*", "/", "//", "%", "**"]:
                # Check if it's unary or binary operation
                if len(ir_node) == 2:
                    return self._convert_unary_op(ir_node)
                else:
                    return self._convert_binary_op(ir_node)
            else:
                # Try to handle as generic expression
                return self._convert_expression(ir_node)
        elif isinstance(ir_node, str):
            # Handle string values - for standalone strings, check if identifier
            if ir_node.isidentifier():
                return ir_node
            else:
                return repr(ir_node)
        else:
            # Handle literals and simple values
            return self._convert_literal(ir_node)

    def _convert_module(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert module IR to source code."""
        _, statements = ir_node
        lines = []
        for stmt in statements:
            converted = self.convert_to_source(stmt, indent_level)
            if converted.strip():  # Don't add empty lines
                lines.append(converted)
        return "\n".join(lines)

    def _convert_name(self, ir_node: Tuple) -> str:
        """Convert name IR node to identifier."""
        _, name = ir_node
        return name

    def _convert_const(self, ir_node: Tuple) -> str:
        """Convert constant IR node to literal value."""
        _, value = ir_node
        return self._convert_literal(value)

    def _convert_const_b(self, ir_node: Tuple) -> str:
        """Convert bytes constant IR node to bytes literal."""
        _, string_value = ir_node
        # Convert string back to bytes representation
        bytes_value = string_value.encode("latin-1")
        return repr(bytes_value)

    def _convert_assign(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert assignment IR to source code."""
        _, target, value, _ = ir_node  # Fourth element is type info (can be None)
        indent = self._get_indent(indent_level)
        # Value in assignment could be literal or expression
        value_str = self._convert_value_in_context(value, "value")
        # Target is always a variable name, so don't quote it
        return f"{indent}{target} = {value_str}"

    def _convert_subscript_assign(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert subscript assignment IR to source code."""
        _, obj, key, value = ir_node
        indent = self._get_indent(indent_level)
        obj_str = self._convert_identifier_or_value(obj)
        key_str = self._convert_value_in_context(key, "value")
        value_str = self._convert_value_in_context(value, "value")
        return f"{indent}{obj_str}[{key_str}] = {value_str}"

    def _convert_aug_assign(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert augmented assignment IR to source code."""
        _, target, op, value = ir_node
        indent = self._get_indent(indent_level)
        target_str = self.convert_to_source(target, 0).strip()
        value_str = self.convert_to_source(value, 0).strip()
        return f"{indent}{target_str} {op} {value_str}"

    def _convert_tuple_assign(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert tuple assignment IR to source code."""
        _, targets, value = ir_node
        indent = self._get_indent(indent_level)
        # Convert targets tuple to comma-separated string
        targets_str = ", ".join(targets)
        # Convert value to source code
        value_str = self._convert_value_in_context(value, "value")
        return f"{indent}{targets_str} = {value_str}"

    def _convert_multi_assign(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert multiple assignment IR to source code."""
        _, assignments = ir_node

        # Extract the value from the first assignment
        first_assign = assignments[0]
        _, _, value, _ = first_assign  # (assign, target, value, type_info)
        value_str = self.convert_to_source(value)

        # Extract all target names
        targets = []
        for assign in assignments:
            _, target, _, _ = assign
            targets.append(target)

        # Create the multiple assignment string: a = b = c = value
        targets_str = " = ".join(targets)
        indent = self._get_indent(indent_level)

        return f"{indent}{targets_str} = {value_str}"

    def _convert_if(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert if statement IR to source code."""
        _, condition, body, orelse = ir_node
        lines = []

        # If condition
        condition_str = self.convert_to_source(condition)
        indent = self._get_indent(indent_level)
        lines.append(f"{indent}if {condition_str}:")

        # If body
        for stmt in body:
            lines.append(self.convert_to_source(stmt, indent_level + 1))

        # Else clause
        if orelse:
            lines.append(f"{indent}else:")
            for stmt in orelse:
                lines.append(self.convert_to_source(stmt, indent_level + 1))

        return "\n".join(lines)

    def _convert_while(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert while loop IR to source code."""
        _, condition, body = ir_node
        lines = []

        condition_str = self.convert_to_source(condition)
        indent = self._get_indent(indent_level)
        lines.append(f"{indent}while {condition_str}:")

        for stmt in body:
            lines.append(self.convert_to_source(stmt, indent_level + 1))

        return "\n".join(lines)

    def _convert_for(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert for loop IR to source code."""
        _, target, iter_val, body, orelse = ir_node
        lines = []

        # Target is always a variable name (identifier)
        target_str = (
            target if isinstance(target, str) else self.convert_to_source(target)
        )
        iter_str = self._convert_identifier_or_value(iter_val)
        indent = self._get_indent(indent_level)
        lines.append(f"{indent}for {target_str} in {iter_str}:")

        for stmt in body:
            lines.append(self.convert_to_source(stmt, indent_level + 1))

        if orelse:
            lines.append(f"{indent}else:")
            for stmt in orelse:
                lines.append(self.convert_to_source(stmt, indent_level + 1))

        return "\n".join(lines)

    def _convert_func_def(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert function definition IR to source code."""
        # Handle both Silu format (4 elements) and C format (5-6 elements)
        if len(ir_node) == 4:
            # Silu format: ("func_def", name, args, body)
            _, name, args, body = ir_node
        elif len(ir_node) >= 5:
            # C format: ("func_def", name, args, body, param_types, [return_type])
            _, name, args, body = ir_node[:4]
        else:
            raise ValueError(
                f"Invalid func_def format: expected 4+ elements, got {len(ir_node)}"
            )
        lines = []

        args_str = ", ".join(str(arg) for arg in args)
        indent = self._get_indent(indent_level)
        lines.append(f"{indent}def {name}({args_str}):")

        for stmt in body:
            lines.append(self.convert_to_source(stmt, indent_level + 1))

        return "\n".join(lines)

    def _convert_class_def(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert class definition IR to source code."""
        _, name, bases, body = ir_node
        lines = []

        indent = self._get_indent(indent_level)

        # Handle base classes if present
        bases_str = ""
        if bases:
            bases_str = (
                "(" + ", ".join(self._convert_expression(base) for base in bases) + ")"
            )

        lines.append(f"{indent}class {name}{bases_str}:")

        if body:
            for stmt in body:
                lines.append(self.convert_to_source(stmt, indent_level + 1))
        else:
            # Empty class needs a pass statement
            lines.append(f"{indent}    pass")

        return "\n".join(lines)

    def _convert_c_for(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert C-style for loop IR to source code."""
        _, init, condition, update, body = ir_node

        indent = self._get_indent(indent_level)
        lines = []

        # Convert components to string
        init_str = self.convert_to_source(init, 0).strip() if init else ""
        cond_str = self.convert_to_source(condition, 0).strip() if condition else ""
        update_str = self.convert_to_source(update, 0).strip() if update else ""

        lines.append(f"{indent}for {init_str}; {cond_str}; {update_str}:")

        # Convert body
        if isinstance(body, (list, tuple)):
            for stmt in body:
                lines.append(self.convert_to_source(stmt, indent_level + 1))
        else:
            lines.append(self.convert_to_source(body, indent_level + 1))

        return "\n".join(lines)

    def _convert_increment_decrement(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert increment/decrement operations IR to source code."""
        op, operand = ir_node

        indent = self._get_indent(indent_level)
        operand_str = self.convert_to_source(operand, 0).strip()

        if op == "p++":
            return f"{indent}{operand_str}++"
        elif op == "p--":
            return f"{indent}{operand_str}--"
        elif op == "++":
            return f"{indent}++{operand_str}"
        elif op == "--":
            return f"{indent}--{operand_str}"
        else:
            return f"{indent}{op} {operand_str}"

    def _convert_return(self, ir_node: Tuple, indent_level: int) -> str:
        """Convert return statement IR to source code."""
        _, value = ir_node
        indent = self._get_indent(indent_level)
        if value is None:
            return f"{indent}return"
        else:
            value_str = self.convert_to_source(value)
            return f"{indent}return {value_str}"

    def _convert_call(self, ir_node: Tuple, indent_level: int = 0) -> str:
        """Convert function call IR to source code."""
        _, func, args, keywords = ir_node
        func_str = self._convert_identifier_or_value(func)

        arg_strs = []
        for arg in args:
            arg_strs.append(self._convert_identifier_or_value(arg))

        # Handle keyword arguments
        for key, value in keywords:
            value_str = self.convert_to_source(value)
            arg_strs.append(f"{key}={value_str}")

        args_str = ", ".join(arg_strs)
        call_str = f"{func_str}({args_str})"

        # If indent_level is provided, treat this as a statement
        if indent_level > 0:
            return self._get_indent(indent_level) + call_str
        else:
            return call_str

    def _convert_lambda(self, ir_node: Tuple) -> str:
        """Convert lambda expression IR to source code."""
        _, args, body = ir_node

        # Convert arguments
        if isinstance(args, tuple):
            args_str = ", ".join(args)
        else:
            args_str = str(args)

        # Convert body expression
        body_str = self.convert_to_source(body)

        return f"lambda {args_str}: {body_str}"

    def _convert_if_expr(self, ir_node: Tuple) -> str:
        """Convert if expression (ternary operator) IR to source code."""
        _, condition, true_val, false_val = ir_node

        condition_str = self.convert_to_source(condition)
        true_str = self.convert_to_source(true_val)
        false_str = self.convert_to_source(false_val)

        return f"{true_str} if {condition_str} else {false_str}"

    def _convert_list(self, ir_node: Tuple) -> str:
        """Convert list IR to source code."""
        _, elements = ir_node
        element_strs = [
            self._convert_value_in_context(elem, "value") for elem in elements
        ]
        return f"[{', '.join(element_strs)}]"

    def _convert_tuple(self, ir_node: Tuple) -> str:
        """Convert tuple IR to source code."""
        _, elements = ir_node
        element_strs = [
            self._convert_value_in_context(elem, "value") for elem in elements
        ]
        if len(elements) == 1:
            return f"({element_strs[0]},)"
        return f"({', '.join(element_strs)})"

    def _convert_dict(self, ir_node: Tuple) -> str:
        """Convert dict IR to source code."""
        _, elements = ir_node
        pairs = []
        for key, value in elements:
            key_str = self._convert_value_in_context(key, "value")
            value_str = self._convert_value_in_context(value, "value")
            pairs.append(f"{key_str}: {value_str}")
        return f"{{{', '.join(pairs)}}}"

    def _convert_set(self, ir_node: Tuple) -> str:
        """Convert set IR to source code."""
        _, elements = ir_node
        element_strs = [
            self._convert_value_in_context(elem, "value") for elem in elements
        ]
        return f"{{{', '.join(element_strs)}}}"

    def _convert_attribute(self, ir_node: Tuple) -> str:
        """Convert attribute access IR to source code."""
        _, obj, attr = ir_node
        obj_str = self._convert_identifier_or_value(obj)
        return f"{obj_str}.{attr}"

    def _convert_subscript(self, ir_node: Tuple) -> str:
        """Convert subscript IR to source code."""
        _, obj, index = ir_node
        obj_str = self._convert_identifier_or_value(obj)
        index_str = self._convert_identifier_or_value(index)
        return f"{obj_str}[{index_str}]"

    def _convert_slice(self, ir_node: Tuple) -> str:
        """Convert slice IR to source code."""
        _, lower, upper, step = ir_node
        parts = []

        if lower is not None:
            parts.append(self.convert_to_source(lower))
        else:
            parts.append("")

        parts.append(":")

        if upper is not None:
            parts.append(self.convert_to_source(upper))
        else:
            parts.append("")

        if step is not None:
            parts.append(":")
            parts.append(self.convert_to_source(step))

        return "".join(parts)

    def _convert_chained_compare(self, ir_node: Tuple) -> str:
        """Convert chained comparison IR to source code."""
        _, comparisons = ir_node
        parts = []

        if comparisons:
            # First comparison
            op, left, right = comparisons[0]
            parts.append(self.convert_to_source(left))
            parts.append(f" {op} ")
            parts.append(self.convert_to_source(right))

            # Subsequent comparisons
            for op, left, right in comparisons[1:]:
                parts.append(f" {op} ")
                parts.append(self.convert_to_source(right))

        return "".join(parts)

    def _convert_binary_op(self, ir_node: Tuple) -> str:
        """Convert binary operation IR to source code."""
        op, left, right = ir_node
        left_str = self._convert_identifier_or_value(left)
        right_str = self._convert_identifier_or_value(right)

        # Add parentheses if needed for nested operations
        if self._needs_parentheses(left, op):
            left_str = f"({left_str})"
        if self._needs_parentheses(right, op):
            right_str = f"({right_str})"

        return f"{left_str} {op} {right_str}"

    def _convert_comparison(self, ir_node: Tuple) -> str:
        """Convert comparison IR to source code."""
        op, left, right = ir_node
        left_str = self._convert_identifier_or_value(left)
        right_str = self._convert_identifier_or_value(right)
        return f"{left_str} {op} {right_str}"

    def _convert_bool_op(self, ir_node: Tuple) -> str:
        """Convert boolean operation IR to source code."""
        op, left, right = ir_node
        left_str = self.convert_to_source(left)
        right_str = self.convert_to_source(right)

        # Add parentheses only if operands need them based on precedence
        if self._needs_parentheses(left, op):
            left_str = f"({left_str})"
        if self._needs_parentheses(right, op):
            right_str = f"({right_str})"

        return f"{left_str} {op} {right_str}"

    def _convert_unary_op(self, ir_node: Tuple) -> str:
        """Convert unary operation IR to source code."""
        op, operand = ir_node
        operand_str = self.convert_to_source(operand)

        # For 'not' operator, add parentheses if operand is a boolean operation
        # that has lower precedence than 'not'
        if op == "not" and self._needs_parentheses(operand, op):
            operand_str = f"({operand_str})"

        if op == "-":
            return f"-{operand_str}"
        elif op == "+":
            return f"+{operand_str}"
        elif op == "not":
            return f"not {operand_str}"
        else:
            return f"{op}{operand_str}"

    def _convert_expression(self, ir_node: Any) -> str:
        """Generic expression converter for unknown node types."""
        if isinstance(ir_node, tuple) and len(ir_node) >= 2:
            # Try to handle as operation
            op = ir_node[0]
            operands = ir_node[1:]

            if len(operands) == 1:
                # Unary operation
                return f"{op}({self.convert_to_source(operands[0])})"
            elif len(operands) == 2:
                # Binary operation
                left_str = self.convert_to_source(operands[0])
                right_str = self.convert_to_source(operands[1])
                return f"{left_str} {op} {right_str}"
            else:
                # Multiple operands
                operand_strs = [self.convert_to_source(op) for op in operands]
                return f"{op}({', '.join(operand_strs)})"

        return str(ir_node)

    def _convert_literal(self, value: Any) -> str:
        """Convert literal values to source code."""
        if isinstance(value, str):
            # Always treat strings that reach here as string literals
            return repr(value)
        elif value is None:
            return "None"
        elif isinstance(value, bool):
            return "True" if value else "False"
        else:
            return str(value)

    def _needs_parentheses(self, operand: Any, parent_op: str) -> bool:
        """Determine if an operand needs parentheses based on operator precedence."""
        if not isinstance(operand, tuple) or len(operand) < 1:
            return False

        operand_op = operand[0]

        # Operator precedence (higher number = higher precedence)
        precedence = {
            "or": 1,
            "and": 2,
            "not": 3,
            "==": 4,
            "!=": 4,
            "<": 4,
            ">": 4,
            "<=": 4,
            ">=": 4,
            "+": 5,
            "-": 5,
            "*": 6,
            "/": 6,
            "//": 6,
            "%": 6,
            "**": 7,
        }

        parent_prec = precedence.get(parent_op, 10)
        operand_prec = precedence.get(operand_op, 10)

        return operand_prec < parent_prec

    def _get_indent(self, level: int) -> str:
        """Get indentation string for given level."""
        return " " * (level * self.indent_size)

    def _convert_identifier_or_value(self, value: Any) -> str:
        """Convert a value that could be an identifier or a literal."""
        if isinstance(value, str):
            # Enhanced heuristics to distinguish identifiers from string literals
            if self._is_likely_identifier(value):
                return value  # Return as identifier
            else:
                return repr(value)  # Return as string literal
        else:
            return self.convert_to_source(value)

    def _is_likely_identifier(self, value: str) -> bool:
        """Determine if a string is likely an identifier rather than a literal."""
        # Must be a valid Python identifier
        if not value.isidentifier():
            return False

        # Common string literal patterns that should be quoted
        string_literal_indicators = [
            # Contains spaces or punctuation that suggests human-readable text
            " ",
            ".",
            "!",
            "?",
            ",",
            ";",
            ":",
            '"',
            "'",
            # Common greeting/message patterns
            "Hello",
            "Hi",
            "Hey",
            "Howdy",
            "Welcome",
            # Common words that appear in messages
            "message",
            "error",
            "warning",
            "info",
            "debug",
        ]

        # If it contains obvious string literal patterns, treat as literal
        for indicator in string_literal_indicators[:9]:  # punctuation/spaces
            if indicator in value:
                return False

        # If it starts with common greeting words, likely a message
        for greeting in string_literal_indicators[9:13]:  # greetings
            if value.startswith(greeting):
                return False

        # Common string literal words (case sensitive)
        literal_words = {
            "Alice",
            "Bob",
            "Charlie",
            "Diana",
            "John",
            "Jane",
            "Doe",
            "Hello",
            "Hi",
            "Hey",
            "Howdy",
            "Good",
            "Bad",
            "Error",
            "Success",
            "positive",
            "negative",
            "zero",
            "large",
            "small",
            "Excellent",
            "New York",
            "Engineer",
            "LOG_",
            "text",
            "more text",
        }

        # Common function names that should be treated as identifiers
        common_function_names = {
            "print",
            "len",
            "max",
            "min",
            "sum",
            "abs",
            "round",
            "sorted",
            "reversed",
            "enumerate",
            "zip",
            "map",
            "filter",
            "range",
            "list",
            "dict",
            "set",
            "tuple",
            "str",
            "int",
            "float",
            "bool",
            "type",
            "isinstance",
            "hasattr",
            "getattr",
            "setattr",
            "open",
            "close",
            "read",
            "write",
            "append",
            "split",
            "join",
            "strip",
            "replace",
            "find",
            "format",
            "upper",
            "lower",
            "startswith",
            "endswith",
            "isdigit",
            "isalpha",
            "isalnum",
            "isspace",
        }

        # If it's a common function name, treat as identifier
        if value in common_function_names:
            return True

        # Common dictionary keys that should be treated as string literals
        common_dict_keys = {
            "name",
            "age",
            "email",
            "id",
            "type",
            "value",
            "config",
            "settings",
            "users",
            "items",
            "title",
            "description",
            "content",
            "status",
            "error",
            "warning",
            "info",
            "debug",
            "log",
            "file",
            "path",
            "url",
            "link",
            "image",
            "html",
            "json",
            "xml",
            "csv",
            "theme",
            "lang",
            "language",
            "locale",
            "timezone",
            "format",
            "width",
            "height",
            "size",
            "length",
            "count",
            "total",
        }

        if value in literal_words or value in common_dict_keys:
            return False

        # Pattern-based checks
        # All caps with underscores (constants that are often string literals in config)
        if value.isupper() and "_" in value:
            return False

        # Capitalized words that aren't typical variable names
        if value[0].isupper() and len(value) > 1:
            # Names/proper nouns are usually string literals
            if not any(char.islower() for char in value[1:]):  # ALL_CAPS
                return False
            # Mixed case proper nouns
            return False

        # If none of the above, likely an identifier
        return True

    def _convert_value_in_context(self, value: Any, context: str) -> str:
        """Convert a value based on its context."""
        if isinstance(value, str):
            if context == "value":
                # In assignment value context, strings are typically literals
                return repr(value)
            elif context == "identifier":
                # In identifier context, return as-is
                return value
            else:
                # Default: check if identifier
                return value if value.isidentifier() else repr(value)
        else:
            return self.convert_to_source(value)


def convert_ir_file_to_source(ir_file_path: str, output_file_path: str = None) -> str:
    """Convert an IR file to source code file."""
    try:
        ir_data = parse_ir_from_file(ir_file_path)
    except (IRParseError, FileNotFoundError) as e:
        raise ValueError(f"Could not parse IR file: {e}")

    # Convert to source
    converter = IRToSourceConverter()
    source_code = converter.convert_to_source(ir_data)

    # Write to output file if specified
    if output_file_path:
        with open(output_file_path, "w") as f:
            f.write(source_code)
            f.write("\n")  # Add final newline

    return source_code


def convert_ir_string_to_source(ir_string: str) -> str:
    """Convert an IR string to source code."""
    try:
        ir_data = parse_ir_from_json_string(ir_string)
    except IRParseError as e:
        raise ValueError(f"Could not parse IR string: {e}")

    # Convert to source
    converter = IRToSourceConverter()
    return converter.convert_to_source(ir_data)


# Convenience functions for shared use with symbolic_executor
def make_expression_readable(expr: Any) -> str:
    """Convert IR expression to readable format (shared with symbolic executor)."""
    converter = IRToSourceConverter()
    return converter.convert_to_source(expr)


def simplify_value_display(value: Any) -> str:
    """Simplify value display for better readability (shared with symbolic executor)."""
    converter = IRToSourceConverter()
    return converter.convert_to_source(value)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ir_to_source.py <ir_file> [output_file]")
        sys.exit(1)

    ir_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        source_code = convert_ir_file_to_source(ir_file, output_file)
        if not output_file:
            print(source_code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
