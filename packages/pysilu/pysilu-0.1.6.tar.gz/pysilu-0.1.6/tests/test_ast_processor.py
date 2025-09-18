"""
Unit tests for the Silu AST processor module.
"""

import ast
import pytest
from silu.ast_processor import BaseASTProcessor


class MockASTProcessor(BaseASTProcessor):
    """Mock implementation of BaseASTProcessor for testing purposes."""

    def __init__(self):
        super().__init__()
        self.results = []

    def process_assign(self, target: str, value):
        """Test implementation of process_assign."""
        return f"assign_{target}={value}"

    def process_aug_assign(self, target, op: str, value):
        """Test implementation of process_aug_assign."""
        return f"aug_assign_{target}{op}{value}"

    def process_tuple_assign(self, targets, value):
        """Test implementation of process_tuple_assign."""
        return f"tuple_assign_{targets}={value}"

    def process_name(self, name: str, context: ast.AST):
        """Test implementation of process_name."""
        if isinstance(context, ast.Load):
            return f"load_{name}"
        elif isinstance(context, ast.Store):
            return f"store_{name}"
        else:
            raise NotImplementedError(f"Unsupported name context: {type(context)}")

    def process_constant(self, value):
        """Test implementation of process_constant."""
        return value

    def process_operation(self, op: str, *operands):
        """Test implementation of process_operation."""
        return f"{op}({','.join(str(o) for o in operands)})"

    def process_call(self, func, args, keywords):
        """Test implementation of process_call."""
        return f"call_{func}({args})"

    def process_control_flow(self, node_type: str, **kwargs):
        """Test implementation of process_control_flow."""
        return f"control_{node_type}"

    def process_container(self, container_type: str, elements):
        """Test implementation of process_container."""
        return f"{container_type}({elements})"

    def process_break_continue(self, statement_type: str):
        """Test implementation of process_break_continue."""
        return f"{statement_type}_stmt"

    def process_assert(self, test, msg=None):
        """Test implementation of process_assert."""
        return f"assert({test}, {msg})"

    def process_ann_assign(self, target: str, value, annotation):
        """Test implementation of process_ann_assign."""
        return f"ann_assign_{target}:{annotation}={value}"

    def process_lambda(self, params, body_node):
        """Test implementation of process_lambda."""
        return f"lambda({params}, {body_node})"

    def process_expr(self, value):
        """Test implementation of process_expr."""
        return f"expr({value})"

    def process_attribute(self, obj, attr):
        """Test implementation of process_attribute."""
        return f"attr({obj}.{attr})"

    def process_subscript(self, obj, index):
        """Test implementation of process_subscript."""
        return f"subscript({obj}[{index}])"

    def process_subscript_assign(self, obj, key, value):
        """Test implementation of process_subscript_assign."""
        return f"subscript_assign({obj}[{key}]={value})"


class TestBaseASTProcessor:
    """Tests for the BaseASTProcessor class."""

    def test_visit_module(self):
        """Test visiting a module node."""
        processor = MockASTProcessor()

        # Create a simple module with an assignment
        assign_target = ast.Name(id="x", ctx=ast.Store())
        assign_value = ast.Constant(value=42)
        assign_node = ast.Assign(targets=[assign_target], value=assign_value)
        module = ast.Module(body=[assign_node], type_ignores=[])

        result = processor.visit_Module(module)
        assert result == "module(['assign_x=42'])"

    def test_visit_expr(self):
        """Test visiting an expression node."""
        processor = MockASTProcessor()

        # Create an expression node
        value = ast.Constant(value=42)
        expr = ast.Expr(value=value)

        result = processor.visit_Expr(expr)
        assert result == "expr(42)"

    def test_visit_assign_simple(self):
        """Test visiting a simple assignment node."""
        processor = MockASTProcessor()

        # Create a simple assignment
        target = ast.Name(id="x", ctx=ast.Store())
        value = ast.Constant(value=42)
        assign = ast.Assign(targets=[target], value=value)

        result = processor.visit_Assign(assign)
        assert result == "assign_x=42"

    def test_visit_assign_multiple_targets(self):
        """Test visiting an assignment with multiple targets."""
        processor = MockASTProcessor()

        # Create assignment with multiple targets
        target1 = ast.Name(id="x", ctx=ast.Store())
        target2 = ast.Name(id="y", ctx=ast.Store())
        value = ast.Constant(value=42)
        assign = ast.Assign(targets=[target1, target2], value=value)

        # Multiple assignment should now work and return the last assignment result
        result = processor.visit_Assign(assign)
        assert result == "assign_y=42"  # Should return the last assignment

    def test_visit_assign_non_name_target(self):
        """Test visiting an assignment with non-name target."""
        processor = MockASTProcessor()

        # Create assignment with non-name target (e.g., attribute)
        target = ast.Attribute(
            value=ast.Name(id="obj", ctx=ast.Load()), attr="attr", ctx=ast.Store()
        )
        value = ast.Constant(value=42)
        assign = ast.Assign(targets=[target], value=value)

        with pytest.raises(
            NotImplementedError,
            match="Assignment to Attribute not supported",
        ):
            processor.visit_Assign(assign)

    def test_visit_assign_subscript(self):
        """Test visiting a subscript assignment."""
        processor = MockASTProcessor()

        # Create subscript assignment: arr[0] = 42
        target = ast.Subscript(
            value=ast.Name(id="arr", ctx=ast.Load()),
            slice=ast.Constant(value=0),
            ctx=ast.Store(),
        )
        value = ast.Constant(value=42)
        assign = ast.Assign(targets=[target], value=value)

        result = processor.visit_Assign(assign)
        assert result == "subscript_assign(load_arr[0]=42)"

    def test_visit_name_load(self):
        """Test visiting a name node with load context."""
        processor = MockASTProcessor()

        name = ast.Name(id="x", ctx=ast.Load())
        result = processor.visit_Name(name)
        assert result == "load_x"

    def test_visit_name_store(self):
        """Test visiting a name node with store context."""
        processor = MockASTProcessor()

        name = ast.Name(id="x", ctx=ast.Store())
        result = processor.visit_Name(name)
        assert result == "store_x"

    def test_visit_constant(self):
        """Test visiting a constant node."""
        processor = MockASTProcessor()

        # Test various constant types
        const_int = ast.Constant(value=42)
        assert processor.visit_Constant(const_int) == 42

        const_str = ast.Constant(value="hello")
        assert processor.visit_Constant(const_str) == "hello"

        const_bool = ast.Constant(value=True)
        assert processor.visit_Constant(const_bool) is True

        const_float = ast.Constant(value=3.14)
        assert processor.visit_Constant(const_float) == 3.14

    def test_visit_binop(self):
        """Test visiting a binary operation node."""
        processor = MockASTProcessor()

        left = ast.Constant(value=5)
        right = ast.Constant(value=3)
        binop = ast.BinOp(left=left, op=ast.Add(), right=right)

        result = processor.visit_BinOp(binop)
        assert result == "+(5,3)"

    def test_visit_unaryop(self):
        """Test visiting a unary operation node."""
        processor = MockASTProcessor()

        operand = ast.Constant(value=5)
        unaryop = ast.UnaryOp(op=ast.USub(), operand=operand)

        result = processor.visit_UnaryOp(unaryop)
        assert result == "-(5)"

    def test_visit_boolop(self):
        """Test visiting a boolean operation node."""
        processor = MockASTProcessor()

        values = [ast.Constant(value=True), ast.Constant(value=False)]
        boolop = ast.BoolOp(op=ast.And(), values=values)

        result = processor.visit_BoolOp(boolop)
        assert result == "and(True,False)"

    def test_visit_compare(self):
        """Test visiting a comparison node."""
        processor = MockASTProcessor()

        left = ast.Constant(value=5)
        comparators = [ast.Constant(value=3)]
        ops = [ast.Lt()]
        compare = ast.Compare(left=left, ops=ops, comparators=comparators)

        result = processor.visit_Compare(compare)
        assert result == "compare(5,['<'],[3])"

    def test_get_operator_supported(self):
        """Test getting supported operators."""
        processor = MockASTProcessor()

        # Test arithmetic operators
        assert processor._get_operator(ast.Add()) == "+"
        assert processor._get_operator(ast.Sub()) == "-"
        assert processor._get_operator(ast.Mult()) == "*"
        assert processor._get_operator(ast.Div()) == "/"
        assert processor._get_operator(ast.FloorDiv()) == "//"
        assert processor._get_operator(ast.Mod()) == "%"
        assert processor._get_operator(ast.Pow()) == "**"

        # Test unary operators
        assert processor._get_operator(ast.UAdd()) == "+"
        assert processor._get_operator(ast.USub()) == "-"
        assert processor._get_operator(ast.Not()) == "not"

        # Test boolean operators
        assert processor._get_operator(ast.And()) == "and"
        assert processor._get_operator(ast.Or()) == "or"

        # Test comparison operators
        assert processor._get_operator(ast.Eq()) == "=="
        assert processor._get_operator(ast.NotEq()) == "!="
        assert processor._get_operator(ast.Lt()) == "<"
        assert processor._get_operator(ast.LtE()) == "<="
        assert processor._get_operator(ast.Gt()) == ">"
        assert processor._get_operator(ast.GtE()) == ">="

    def test_get_operator_unsupported(self):
        """Test getting unsupported operators."""
        processor = MockASTProcessor()

        # Test unsupported operator
        with pytest.raises(NotImplementedError, match="Unsupported operator: LShift"):
            processor._get_operator(ast.LShift())

    def test_visit_call_builtin(self):
        """Test visiting a function call node with built-in function."""
        processor = MockASTProcessor()

        # Create a call to print function
        func = ast.Name(id="print", ctx=ast.Load())
        args = [ast.Constant(value="hello")]
        call = ast.Call(func=func, args=args, keywords=[])

        result = processor.visit_Call(call)
        assert result == "call_load_print(['hello'])"

    def test_visit_if(self):
        """Test visiting an if statement."""
        processor = MockASTProcessor()

        # Create an if statement
        test = ast.Constant(value=True)
        body = [ast.Expr(value=ast.Constant(value=1))]
        orelse = [ast.Expr(value=ast.Constant(value=2))]
        if_stmt = ast.If(test=test, body=body, orelse=orelse)

        result = processor.visit_If(if_stmt)
        assert result == "control_if"

    def test_visit_while(self):
        """Test visiting a while statement."""
        processor = MockASTProcessor()

        # Create a while statement
        test = ast.Constant(value=True)
        body = [ast.Expr(value=ast.Constant(value=1))]
        while_stmt = ast.While(test=test, body=body, orelse=[])

        result = processor.visit_While(while_stmt)
        assert result == "control_while"

    def test_visit_for(self):
        """Test visiting a for statement."""
        processor = MockASTProcessor()

        # Create a for statement
        target = ast.Name(id="i", ctx=ast.Store())
        iter_node = ast.List(
            elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load()
        )
        body = [ast.Expr(value=ast.Name(id="i", ctx=ast.Load()))]
        for_stmt = ast.For(target=target, iter=iter_node, body=body, orelse=[])

        result = processor.visit_For(for_stmt)
        assert result == "control_for"

    def test_visit_functiondef(self):
        """Test visiting a function definition."""
        processor = MockASTProcessor()

        # Create a function definition
        args = ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg="x", annotation=None)],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )
        body = [ast.Return(value=ast.Name(id="x", ctx=ast.Load()))]
        funcdef = ast.FunctionDef(
            name="test_func", args=args, body=body, decorator_list=[], returns=None
        )

        result = processor.visit_FunctionDef(funcdef)
        assert result == "control_function_def"

    def test_visit_return(self):
        """Test visiting a return statement."""
        processor = MockASTProcessor()

        # Create a return statement
        return_stmt = ast.Return(value=ast.Constant(value=42))

        result = processor.visit_Return(return_stmt)
        assert result == "control_return"

    def test_visit_aug_assign_simple(self):
        """Test visiting a simple augmented assignment node."""
        processor = MockASTProcessor()

        # Create an augmented assignment: x += 5
        aug_assign = ast.AugAssign(
            target=ast.Name(id="x", ctx=ast.Store()),
            op=ast.Add(),
            value=ast.Constant(value=5),
        )

        result = processor.visit_AugAssign(aug_assign)
        assert result == "aug_assign_store_x+5"

    def test_visit_aug_assign_subscript(self):
        """Test visiting a subscript augmented assignment node."""
        processor = MockASTProcessor()

        # Create an augmented assignment: arr[0] -= 3
        aug_assign = ast.AugAssign(
            target=ast.Subscript(
                value=ast.Name(id="arr", ctx=ast.Load()),
                slice=ast.Constant(value=0),
                ctx=ast.Store(),
            ),
            op=ast.Sub(),
            value=ast.Constant(value=3),
        )

        result = processor.visit_AugAssign(aug_assign)
        assert result == "aug_assign_('load_arr', 0)-3"

    def test_visit_aug_assign_unsupported_target(self):
        """Test visiting an augmented assignment with unsupported target."""
        processor = MockASTProcessor()

        # Create an augmented assignment with unsupported target (attribute)
        aug_assign = ast.AugAssign(
            target=ast.Attribute(
                value=ast.Name(id="obj", ctx=ast.Load()), attr="attr", ctx=ast.Store()
            ),
            op=ast.Add(),
            value=ast.Constant(value=1),
        )

        with pytest.raises(
            NotImplementedError, match="Augmented assignment to Attribute not supported"
        ):
            processor.visit_AugAssign(aug_assign)

    def test_visit_assign_tuple_unpacking(self):
        """Test visiting a tuple unpacking assignment."""
        processor = MockASTProcessor()

        # Create tuple unpacking assignment: a, b = 1, 2
        targets = ast.Tuple(
            elts=[ast.Name(id="a", ctx=ast.Store()), ast.Name(id="b", ctx=ast.Store())],
            ctx=ast.Store(),
        )
        value = ast.Tuple(
            elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load()
        )
        assign = ast.Assign(targets=[targets], value=value)

        result = processor.visit_Assign(assign)
        assert result == "tuple_assign_['a', 'b']=tuple((1, 2))"

    def test_visit_assign_tuple_unpacking_non_name_target(self):
        """Test visiting tuple unpacking with non-name target."""
        processor = MockASTProcessor()

        # Create tuple unpacking with non-name target
        targets = ast.Tuple(
            elts=[
                ast.Name(id="a", ctx=ast.Store()),
                ast.Attribute(
                    value=ast.Name(id="obj", ctx=ast.Load()),
                    attr="attr",
                    ctx=ast.Store(),
                ),
            ],
            ctx=ast.Store(),
        )
        value = ast.Tuple(
            elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load()
        )
        assign = ast.Assign(targets=[targets], value=value)

        with pytest.raises(
            NotImplementedError,
            match="Only simple names are supported in tuple unpacking",
        ):
            processor.visit_Assign(assign)
