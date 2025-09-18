"""
Abstract Base Class for AST Processing

This module provides a common base class for both interpretation and IR generation,
extracting shared AST traversal logic while allowing customization of processing behavior.
"""

import ast
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseASTProcessor(ast.NodeVisitor, ABC):
    """
    Abstract base class for AST processing.

    This class provides common AST traversal logic and defines abstract methods
    that subclasses must implement to customize processing behavior.
    """

    # Consolidated operators mapping
    OPERATORS = {
        # Binary operators
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.FloorDiv: "//",
        ast.Mod: "%",
        ast.Pow: "**",
        # Unary operators
        ast.UAdd: "+",
        ast.USub: "-",
        ast.Not: "not",
        # Comparison operators
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
        # Boolean operators
        ast.And: "and",
        ast.Or: "or",
    }

    # ================== Abstract Methods ==================

    @abstractmethod
    def process_assign(self, target: Any, value: Any) -> Any:
        """Process an assignment operation."""
        pass

    @abstractmethod
    def process_tuple_assign(self, targets: List[str], value: Any) -> Any:
        """Process a tuple unpacking assignment operation."""
        pass

    @abstractmethod
    def process_subscript_assign(self, obj: Any, key: Any, value: Any) -> Any:
        """Process a subscript assignment operation (e.g., obj[key] = value)."""
        pass

    @abstractmethod
    def process_name(self, name: str, context: ast.AST) -> Any:
        """Process a name/variable reference."""
        pass

    @abstractmethod
    def process_constant(self, value: Any) -> Any:
        """Process a constant value."""
        pass

    @abstractmethod
    def process_operation(self, op: str, *operands) -> Any:
        """Process any operation (binary, unary, boolean, comparison)."""
        pass

    @abstractmethod
    def process_call(self, func: Any, args: List[Any], keywords: Dict[str, Any]) -> Any:
        """Process a function call."""
        pass

    @abstractmethod
    def process_control_flow(self, node_type: str, **kwargs) -> Any:
        """Process control flow statements (if, while, for, return, function def)."""
        pass

    @abstractmethod
    def process_container(self, container_type: str, elements: List[Any]) -> Any:
        """Process containers (list, tuple, etc.)."""
        pass

    @abstractmethod
    def process_expr(self, value: Any) -> Any:
        """Process an expression statement."""
        pass

    @abstractmethod
    def process_attribute(self, obj: Any, attr: str) -> Any:
        """Process attribute access."""
        pass

    @abstractmethod
    def process_subscript(self, obj: Any, index: Any) -> Any:
        """Process subscript operation."""
        pass

    @abstractmethod
    def process_break_continue(self, statement_type: str) -> Any:
        """Process break/continue statements."""
        pass

    @abstractmethod
    def process_assert(self, test: Any, msg: Any = None) -> Any:
        """Process assert statements."""
        pass

    @abstractmethod
    def process_ann_assign(self, target: str, value: Any, annotation: Any) -> Any:
        """Process annotated assignment."""
        pass

    @abstractmethod
    def process_aug_assign(self, target: Any, op: str, value: Any) -> Any:
        """Process augmented assignment (e.g., +=, -=, *=)."""
        pass

    @abstractmethod
    def process_lambda(self, params: List[str], body_node: ast.AST) -> Any:
        """Process lambda function."""
        pass

    # ================== Generic Visit Methods ==================

    def visit_Module(self, node: ast.Module) -> Any:
        """Visit a module node."""
        statements = [self.visit(stmt) for stmt in node.body]
        return self.process_container("module", statements)

    def visit_Expr(self, node: ast.Expr) -> Any:
        """Visit an expression statement."""
        return self.process_expr(self.visit(node.value))

    def visit_Assign(self, node: ast.Assign) -> Any:
        """Visit an assignment node."""
        value = self.visit(node.value)

        # Handle multiple targets (a = b = c = value)
        results = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Simple variable assignment: x = value
                result = self.process_assign(target.id, value)
                results.append(result)
            elif isinstance(target, ast.Subscript):
                # Subscript assignment: obj[key] = value
                obj = self.visit(target.value)
                key = self.visit(target.slice)
                result = self.process_subscript_assign(obj, key, value)
                results.append(result)
            elif isinstance(target, ast.Tuple):
                # Tuple unpacking assignment: a, b = value
                target_names = []
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        target_names.append(elt.id)
                    else:
                        raise NotImplementedError(
                            "Only simple names are supported in tuple unpacking"
                        )
                result = self.process_tuple_assign(target_names, value)
                results.append(result)
            else:
                raise NotImplementedError(
                    f"Assignment to {type(target).__name__} not supported"
                )

        # Return the last result (consistent with Python behavior)
        return results[-1] if results else None

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        """Visit an augmented assignment node."""
        target = node.target
        op = self._get_operator(node.op)
        value = self.visit(node.value)

        if isinstance(target, ast.Name):
            # Simple variable augmented assignment: x += value
            target_processed = self.visit(target)
            return self.process_aug_assign(target_processed, op, value)
        elif isinstance(target, ast.Subscript):
            # Subscript augmented assignment: obj[key] += value
            obj = self.visit(target.value)
            key = self.visit(target.slice)
            return self.process_aug_assign((obj, key), op, value)
        else:
            raise NotImplementedError(
                f"Augmented assignment to {type(target).__name__} not supported"
            )

    def visit_Name(self, node: ast.Name) -> Any:
        """Visit a name node."""
        return self.process_name(node.id, node.ctx)

    def visit_Constant(self, node: ast.Constant) -> Any:
        """Visit a constant node."""
        return self.process_constant(node.value)

    # ================== Operation Handlers ==================

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        """Visit a binary operation node."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = self._get_operator(node.op)
        return self.process_operation(op, left, right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        """Visit a unary operation node."""
        operand = self.visit(node.operand)
        op = self._get_operator(node.op)
        return self.process_operation(op, operand)

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        """Visit a boolean operation node."""
        values = [self.visit(value) for value in node.values]
        op = self._get_operator(node.op)
        return self.process_operation(op, *values)

    def visit_Compare(self, node: ast.Compare) -> Any:
        """Visit a comparison node."""
        left = self.visit(node.left)
        comparators = [self.visit(comp) for comp in node.comparators]
        ops = [self._get_operator(op) for op in node.ops]
        return self.process_operation("compare", left, ops, comparators)

    def visit_Call(self, node: ast.Call) -> Any:
        """Visit a function call node."""
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        keywords = {kw.arg: self.visit(kw.value) for kw in node.keywords}
        return self.process_call(func, args, keywords)

    # ================== Control Flow Handlers ==================

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Visit a function definition node."""
        args = [arg.arg for arg in node.args.args]
        body = node.body
        type_params = [arg.annotation for arg in node.args.args]
        returns = node.returns if hasattr(node, "returns") else None
        return self.process_control_flow(
            "function_def",
            name=node.name,
            args=args,
            body=body,
            type_params=type_params,
            returns=returns,
        )

    def visit_Return(self, node: ast.Return) -> Any:
        """Visit a return statement node."""
        value = self.visit(node.value) if node.value else None
        return self.process_control_flow("return", value=value)

    def visit_If(self, node: ast.If) -> Any:
        """Visit an if statement node."""
        test = self.visit(node.test)
        body = node.body
        orelse = node.orelse if node.orelse else []
        return self.process_control_flow("if", test=test, body=body, orelse=orelse)

    def visit_While(self, node: ast.While) -> Any:
        """Visit a while loop node."""
        test_node = node.test
        body = node.body
        return self.process_control_flow("while", test_node=test_node, body=body)

    def visit_For(self, node: ast.For) -> Any:
        """Visit a for loop node."""
        # Handle tuple unpacking targets
        if isinstance(node.target, ast.Tuple):
            # Extract variable names from tuple elements
            target_names = []
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    target_names.append(elt.id)
                else:
                    raise NotImplementedError(
                        "Only simple names are supported in tuple unpacking"
                    )
            target = ("tuple_unpack", target_names)
        else:
            target = self.visit(node.target)

        iter_ = self.visit(node.iter)
        body = node.body
        orelse = node.orelse if node.orelse else []
        return self.process_control_flow(
            "for", target=target, iter=iter_, body=body, orelse=orelse
        )

    def visit_List(self, node: ast.List) -> Any:
        """Visit a list literal node."""
        elements = [self.visit(element) for element in node.elts]
        return self.process_container("list", elements)

    # ================== Helper Methods ==================

    def _get_operator(self, op: ast.AST) -> str:
        """Get the string representation of an operator."""
        op_str = self.OPERATORS.get(type(op))
        if op_str is None:
            raise NotImplementedError(f"Unsupported operator: {type(op).__name__}")
        return op_str

    def _make_node(self, node_type: str, *args) -> tuple:
        """Helper to create IR nodes consistently."""
        return (node_type, *args)

    def validate_operation(self, op: str, *operands) -> None:
        """Validate operations before processing."""
        if op in ("/", "//", "%") and len(operands) == 2 and operands[1] == 0:
            raise ZeroDivisionError(
                "Division by zero" if op != "%" else "Modulo by zero"
            )

        # Memory protection: prevent operations that could cause out-of-memory
        if op == "*" and len(operands) == 2:
            left, right = operands

            # Check for large number * sequence operations
            if isinstance(left, (list, tuple, str)) and isinstance(right, int):
                if right > 1000000:  # 1M element limit
                    raise MemoryError(
                        f"Memory protection: Cannot multiply sequence by {right} (limit: 1,000,000)"
                    )
                if len(left) * right > 10000000:  # 10M total elements limit
                    raise MemoryError(
                        f"Memory protection: Result would have {len(left) * right} elements (limit: 10,000,000)"
                    )

            elif isinstance(right, (list, tuple, str)) and isinstance(left, int):
                if left > 1000000:  # 1M element limit
                    raise MemoryError(
                        f"Memory protection: Cannot multiply sequence by {left} (limit: 1,000,000)"
                    )
                if len(right) * left > 10000000:  # 10M total elements limit
                    raise MemoryError(
                        f"Memory protection: Result would have {len(right) * left} elements (limit: 10,000,000)"
                    )

    # ================== Shared Node Processing Methods ==================

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        """Handle attribute access."""
        obj = self.visit(node.value)
        return self.process_attribute(obj, node.attr)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        """Handle indexing operations."""
        obj = self.visit(node.value)
        index = self.visit(node.slice)
        return self.process_subscript(obj, index)

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        """Handle tuple literals."""
        elements = tuple(self.visit(element) for element in node.elts)
        return self.process_container("tuple", elements)

    def visit_Dict(self, node: ast.Dict) -> Any:
        """Handle dictionary literals."""
        pairs = []
        for key_node, value_node in zip(node.keys, node.values):
            key = self.visit(key_node) if key_node else None
            value = self.visit(value_node)
            pairs.append((key, value))
        return self.process_container("dict", pairs)

    # ================== Extended Control Flow Handlers ==================

    def visit_Break(self, node: ast.Break) -> Any:
        """Visit a break statement node."""
        return self.process_break_continue("break")

    def visit_Continue(self, node: ast.Continue) -> Any:
        """Visit a continue statement node."""
        return self.process_break_continue("continue")

    def visit_Assert(self, node: ast.Assert) -> Any:
        """Visit an assert statement node."""
        test = self.visit(node.test)
        msg = self.visit(node.msg) if node.msg else None
        return self.process_assert(test, msg)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        """Visit an annotated assignment node."""
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                "Only simple variable annotation assignments supported"
            )
        target = node.target.id
        value = self.visit(node.value) if node.value else None
        annotation = self.visit(node.annotation) if node.annotation else None
        return self.process_ann_assign(target, value, annotation)

    def visit_Lambda(self, node: ast.Lambda) -> Any:
        """Visit a lambda function node."""
        params = [arg.arg for arg in node.args.args]
        body_node = node.body
        return self.process_lambda(params, body_node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """Visit a class definition node."""
        name = node.name
        # Just pass the base nodes directly to process_control_flow
        # This prevents calling visit on dict objects that lack _fields
        bases = node.bases
        body = node.body
        return self.process_control_flow("class_def", name=name, bases=bases, body=body)


def create_processor(processor_type: str, **kwargs) -> BaseASTProcessor:
    """Factory function to create AST processors."""
    if processor_type == "interpreter":
        from .interpreter import SiluInterpreter

        return SiluInterpreter(**kwargs)
    elif processor_type == "ir_generator":
        from .ir_generator import SiluIRGenerator

        return SiluIRGenerator(**kwargs)
    else:
        raise ValueError(f"Unsupported processor type: {processor_type}")


def process_code(
    source_code: str, processor_type: str = "interpreter", **kwargs
) -> Any:
    """Process source code using the specified processor type."""
    tree = ast.parse(source_code)
    processor = create_processor(processor_type, **kwargs)
    return processor.visit(tree)
