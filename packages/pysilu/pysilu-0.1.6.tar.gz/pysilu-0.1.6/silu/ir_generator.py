"""
Silu IR Generator Module - Simplified Implementation

This module provides a streamlined IR generator that extends BaseASTProcessor
to convert Silu programs into intermediate representation.
"""

import ast
from typing import Any, Dict, List, Tuple

from .ast_processor import BaseASTProcessor


class SiluIRGenerator(BaseASTProcessor):
    """Simplified Silu IR generator that converts AST to intermediate representation."""

    def __init__(self, record_types: bool = True):
        self.record_types = record_types

    # ================== Abstract Method Implementations ==================

    def process_assign(self, target: str, value: Any) -> Tuple[str, str, Any, None]:
        """Generate assignment IR node."""
        return ("assign", target, value, None)

    def process_tuple_assign(self, targets: List[str], value: Any) -> Tuple:
        """Generate tuple unpacking assignment IR node."""
        return ("tuple_assign", tuple(targets), value)

    def process_subscript_assign(self, obj: Any, key: Any, value: Any) -> Tuple:
        """Generate subscript assignment IR node."""
        return ("subscript_assign", obj, key, value)

    def process_aug_assign(self, target: Any, op: str, value: Any) -> Tuple:
        """Generate augmented assignment IR node."""
        if isinstance(target, tuple) and len(target) == 2 and target[0] == "name":
            # Simple variable augmented assignment: x += value
            return ("aug_assign", target, op, value)
        elif (
            isinstance(target, tuple)
            and len(target) == 2
            and not isinstance(target[0], str)
        ):
            # Subscript augmented assignment: obj[key] += value
            # target is (obj_ir_node, key_ir_node)
            obj, key = target
            return ("subscript_aug_assign", obj, key, op, value)
        else:
            raise NotImplementedError(
                f"Unsupported augmented assignment target: {target}"
            )

    def process_name(self, name: str, context: ast.AST) -> Tuple[str, str]:
        """Return identifier with type information for IR."""
        return ("name", name)

    def process_constant(self, value: Any) -> Tuple[str, Any]:
        """Return constant value with type information for IR."""
        if isinstance(value, bytes):
            # Handle bytes objects specially for JSON serialization
            return ("const_b", value.decode("latin-1"))
        return ("const", value)

    def process_operation(self, op: str, *operands) -> Tuple:
        """Generate operation IR nodes."""
        if len(operands) == 1:  # Unary
            return (op, operands[0])
        elif len(operands) == 2:  # Binary
            return (op, operands[0], operands[1])
        elif op == "compare":  # Comparison
            left, ops, comparators = operands
            if len(ops) == 1 and len(comparators) == 1:
                return (ops[0], left, comparators[0])
            else:
                # Chained comparisons
                comparisons = []
                current_left = left
                for op_str, comp in zip(ops, comparators):
                    comparisons.append((op_str, current_left, comp))
                    current_left = comp
                return ("chained_compare", tuple(comparisons))
        else:  # Boolean operation
            return tuple([op] + list(operands))

    def process_call(
        self, func: Any, args: List[Any], keywords: Dict[str, Any]
    ) -> Tuple:
        """Generate function call IR node."""
        # Convert to tuples for consistent IR format
        args_tuple = tuple(args)
        keywords_tuple = tuple(keywords.items()) if keywords else ()
        return ("call", func, args_tuple, keywords_tuple)

    def process_control_flow(self, node_type: str, **kwargs) -> Tuple:
        """Generate control flow IR nodes."""
        if node_type == "function_def":
            # Process function body statements
            body = tuple(self.visit(stmt) for stmt in kwargs["body"])
            type_params = tuple(
                self.visit(stmt) if stmt else None for stmt in kwargs["type_params"]
            )
            returns = (
                self.visit(kwargs["returns"])
                if "returns" in kwargs and kwargs["returns"]
                else None
            )
            return (
                "func_def",
                kwargs["name"],
                tuple(kwargs["args"]),
                body,
                type_params,
                returns,
            )
        elif node_type == "class_def":
            # Process class body statements
            body = tuple(self.visit(stmt) for stmt in kwargs["body"])
            bases = tuple(base for base in kwargs["bases"])

            # Collect class attributes and methods
            class_attrs = {}
            for stmt in body:
                if (
                    isinstance(stmt, tuple)
                    and stmt[0] == "ann_assign"
                    and len(stmt) >= 3
                ):
                    # Handle annotated assignments as class attributes
                    attr_name = stmt[1]
                    class_attrs[attr_name] = stmt

            return (
                "class_def",
                kwargs["name"],
                bases,
                body,
            )
        elif node_type == "return":
            return ("return", kwargs["value"])
        elif node_type == "if":
            # Process if statement body and orelse
            body = tuple(self.visit(stmt) for stmt in kwargs["body"])
            orelse = (
                tuple(self.visit(stmt) for stmt in kwargs["orelse"])
                if kwargs["orelse"]
                else ()
            )
            return ("if", kwargs["test"], body, orelse)
        elif node_type == "while":
            # Process test_node ourselves for IR generation
            test = self.visit(kwargs["test_node"])
            body = tuple(self.visit(stmt) for stmt in kwargs["body"])
            return ("while", test, body)
        elif node_type == "for":
            body = tuple(self.visit(stmt) for stmt in kwargs["body"])
            orelse = (
                tuple(self.visit(stmt) for stmt in kwargs["orelse"])
                if kwargs["orelse"]
                else ()
            )
            return ("for", kwargs["target"], kwargs["iter"], body, orelse)

    def process_container(self, container_type: str, elements: List[Any]) -> Tuple:
        """Generate container IR nodes."""
        if container_type == "list":
            return ("list", tuple(elements))
        elif container_type == "tuple":
            return self._make_node("tuple", tuple(elements))
        elif container_type == "dict":
            return self._make_node("dict", tuple(elements))
        elif container_type == "module":
            return ("module", tuple(elements))

    def process_expr(self, value: Any) -> Any:
        """Process expression statements."""
        return value

    def process_attribute(self, obj: Any, attr: str) -> Tuple:
        """Process attribute access."""
        return ("attribute", obj, attr)

    def process_subscript(self, obj: Any, index: Any) -> Tuple:
        """Process subscript operation."""
        return self._make_node("subscript", obj, index)

    def process_break_continue(self, statement_type: str) -> Tuple:
        """Process break/continue statements."""
        return (statement_type,)

    def process_assert(self, test: Any, msg: Any = None) -> Tuple:
        """Process assert statements."""
        return self._make_node("assert", test, msg)

    def process_ann_assign(self, target: str, value: Any, annotation: Any) -> Tuple:
        """Process annotated assignment."""
        return self._make_node("ann_assign", target, value, annotation)

    def process_lambda(self, params: List[str], body_node: ast.AST) -> Tuple:
        """Process lambda function."""
        body = self.visit(body_node)
        return self._make_node("lambda", tuple(params), body)

    # ================== Assignment Overrides for IR Generation ==================

    def visit_Assign(self, node: ast.Assign) -> Any:
        """Override assignment to handle multiple targets for IR generation."""
        value = self.visit(node.value)

        # For multiple targets, we need to generate separate assign nodes
        if len(node.targets) > 1:
            # Generate a list of assignment IR nodes
            assignments = []
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.append(self.process_assign(target.id, value))
                elif isinstance(target, ast.Subscript):
                    obj = self.visit(target.value)
                    key = self.visit(target.slice)
                    assignments.append(self.process_subscript_assign(obj, key, value))
                elif isinstance(target, ast.Tuple):
                    target_names = []
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            target_names.append(elt.id)
                        else:
                            raise NotImplementedError(
                                "Only simple names are supported in tuple unpacking"
                            )
                    assignments.append(self.process_tuple_assign(target_names, value))
                else:
                    raise NotImplementedError(
                        f"Assignment to {type(target).__name__} not supported"
                    )

            # Return a multi-assign node containing all assignments
            return ("multi_assign", tuple(assignments))
        else:
            # Single target - use the base class implementation
            return super().visit_Assign(node)

    # ================== Additional IR Generation Methods ==================

    def visit_AugAssign(self, node: ast.AugAssign) -> Tuple:
        """Generate augmented assignment IR."""
        target = self.visit(node.target)
        op = self.OPERATORS.get(type(node.op), "?")
        value = self.visit(node.value)
        return self._make_node("aug_assign", target, f"{op}=", value)

    def visit_Slice(self, node: ast.Slice) -> Tuple:
        """Generate slice IR."""
        lower = self.visit(node.lower) if node.lower else None
        upper = self.visit(node.upper) if node.upper else None
        step = self.visit(node.step) if node.step else None
        return self._make_node("slice", lower, upper, step)

    def visit_Set(self, node: ast.Set) -> Tuple:
        """Generate set IR."""
        elements = tuple(self.visit(e) for e in node.elts)
        return self._make_node("set", elements)

    # ================== Control Flow Extensions ==================

    def visit_Pass(self, node: ast.Pass) -> Tuple:
        """Generate pass statement IR."""
        return ("pass",)

    # ================== Comprehensions ==================

    def _visit_comprehension(self, comp_type: str, node) -> Tuple:
        """Generic comprehension visitor."""
        if comp_type == "list":
            elt = self.visit(node.elt)
        elif comp_type == "set":
            elt = self.visit(node.elt)
        elif comp_type == "dict":
            key = self.visit(node.key)
            value = self.visit(node.value)
            elt = (key, value)

        generators = []
        for gen in node.generators:
            target = self.visit(gen.target)
            iter_val = self.visit(gen.iter)
            ifs = tuple(self.visit(cond) for cond in gen.ifs)
            generators.append((target, iter_val, ifs))

        return self._make_node(f"{comp_type}_comp", elt, tuple(generators))

    def visit_ListComp(self, node: ast.ListComp) -> Tuple:
        """Generate list comprehension IR."""
        return self._visit_comprehension("list", node)

    def visit_SetComp(self, node: ast.SetComp) -> Tuple:
        """Generate set comprehension IR."""
        return self._visit_comprehension("set", node)

    def visit_DictComp(self, node: ast.DictComp) -> Tuple:
        """Generate dictionary comprehension IR."""
        return self._visit_comprehension("dict", node)

    # ================== Advanced Features ==================

    def visit_IfExp(self, node: ast.IfExp) -> Tuple:
        """Generate conditional expression IR."""
        test = self.visit(node.test)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        return self._make_node("if_expr", test, body, orelse)

    def visit_Starred(self, node: ast.Starred) -> Tuple:
        """Generate starred expression IR."""
        value = self.visit(node.value)
        return self._make_node("starred", value)

    def visit_Yield(self, node: ast.Yield) -> Tuple:
        """Generate yield expression IR."""
        value = self.visit(node.value) if node.value else None
        return self._make_node("yield", value)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> Tuple:
        """Generate yield from expression IR."""
        value = self.visit(node.value)
        return self._make_node("yield_from", value)

    # ================== Exception Handling ==================

    def visit_Try(self, node: ast.Try) -> Tuple:
        """Generate try-except IR."""
        body = tuple(self.visit(stmt) for stmt in node.body)
        handlers = tuple(self.visit(h) for h in node.handlers)
        orelse = tuple(self.visit(stmt) for stmt in node.orelse) if node.orelse else ()
        finalbody = (
            tuple(self.visit(stmt) for stmt in node.finalbody) if node.finalbody else ()
        )
        return self._make_node("try", body, handlers, orelse, finalbody)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Tuple:
        """Generate exception handler IR."""
        exc_type = self.visit(node.type) if node.type else None
        name = node.name if node.name else None
        body = tuple(self.visit(stmt) for stmt in node.body)
        return self._make_node("except", exc_type, name, body)

    def visit_Raise(self, node: ast.Raise) -> Tuple:
        """Generate raise statement IR."""
        exc = self.visit(node.exc) if node.exc else None
        return self._make_node("raise", exc)

    # ================== Import Statements ==================

    def visit_Import(self, node: ast.Import) -> Tuple:
        """Generate import statement IR."""
        names = [(alias.name, alias.asname) for alias in node.names]
        return self._make_node("import", tuple(names))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Tuple:
        """Generate from-import statement IR."""
        module = node.module
        names = [(alias.name, alias.asname) for alias in node.names]
        level = node.level
        return self._make_node("from_import", module, tuple(names), level)

    # ================== Context Managers ==================

    def visit_With(self, node: ast.With) -> Tuple:
        """Generate with statement IR."""
        items = []
        for item in node.items:
            context_expr = self.visit(item.context_expr)
            optional_vars = (
                self.visit(item.optional_vars) if item.optional_vars else None
            )
            items.append((context_expr, optional_vars))
        body = tuple(self.visit(stmt) for stmt in node.body)
        return self._make_node("with", tuple(items), body)

    # ================== Match Statements ==================

    def visit_Match(self, node: ast.Match) -> Tuple:
        """Generate match statement IR."""
        subject = self.visit(node.subject)
        cases = tuple(self.visit(case) for case in node.cases)
        return self._make_node("match", subject, cases)

    def visit_match_case(self, node: ast.match_case) -> Tuple:
        """Generate match case IR."""
        pattern = self.visit(node.pattern)
        guard = self.visit(node.guard) if node.guard else None
        body = tuple(self.visit(stmt) for stmt in node.body)
        return self._make_node("match_case", pattern, guard, body)

    # ================== Match Patterns ==================

    def visit_MatchValue(self, node: ast.MatchValue) -> Tuple:
        """Generate match value pattern IR."""
        value = self.visit(node.value)
        return self._make_node("match_value", value)

    def visit_MatchAs(self, node: ast.MatchAs) -> Tuple:
        """Generate match as pattern IR (wildcard or capture)."""
        pattern = self.visit(node.pattern) if node.pattern else None
        name = node.name if node.name else None
        return self._make_node("match_as", pattern, name)

    def visit_MatchOr(self, node: ast.MatchOr) -> Tuple:
        """Generate match or pattern IR."""
        patterns = tuple(self.visit(pattern) for pattern in node.patterns)
        return self._make_node("match_or", patterns)

    def visit_MatchSequence(self, node: ast.MatchSequence) -> Tuple:
        """Generate match sequence pattern IR."""
        patterns = tuple(self.visit(pattern) for pattern in node.patterns)
        return self._make_node("match_sequence", patterns)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> Tuple:
        """Generate match mapping pattern IR."""
        keys = tuple(self.visit(key) for key in node.keys)
        patterns = tuple(self.visit(pattern) for pattern in node.patterns)
        rest = node.rest if node.rest else None
        return self._make_node("match_mapping", keys, patterns, rest)

    def visit_MatchClass(self, node: ast.MatchClass) -> Tuple:
        """Generate match class pattern IR."""
        cls = self.visit(node.cls)
        patterns = tuple(self.visit(pattern) for pattern in node.patterns)
        kwd_attrs = tuple(node.kwd_attrs) if node.kwd_attrs else ()
        kwd_patterns = tuple(self.visit(pattern) for pattern in node.kwd_patterns)
        return self._make_node("match_class", cls, patterns, kwd_attrs, kwd_patterns)

    def visit_MatchStar(self, node: ast.MatchStar) -> Tuple:
        """Generate match star pattern IR."""
        name = node.name if node.name else None
        return self._make_node("match_star", name)

    def visit_MatchSingleton(self, node: ast.MatchSingleton) -> Tuple:
        """Generate match singleton pattern IR (True, False, None)."""
        value = node.value
        return self._make_node("match_singleton", value)

    # ================== Error Handling ==================

    def generic_visit(self, node: ast.AST) -> None:
        """Handle unsupported AST nodes."""
        # Provide more helpful error message for common node types
        if isinstance(node, ast.ClassDef):
            # This should not happen as we now handle ClassDef
            raise NotImplementedError(
                f"Class definition issue: {node.name}. Check implementation."
            )
        raise NotImplementedError(
            f"Unsupported syntax for IR generation: {type(node).__name__}"
        )
