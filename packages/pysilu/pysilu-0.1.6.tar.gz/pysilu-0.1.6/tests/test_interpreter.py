"""
Unit tests for the Silu interpreter components using pytest.
"""

import ast
import pytest
from silu.interpreter import Environment, SiluInterpreter, Function, ReturnException


class TestEnvironment:
    """Tests for the Environment class."""

    def test_environment_operations(self):
        # Test default environment with built-ins
        env = Environment()
        assert "print" in env.vars
        assert env.parent is None

        # Test parent environment and variable operations
        parent_env = Environment()
        parent_env.set("y", 20)
        child_env = Environment(parent=parent_env)

        child_env.set("x", 10)
        child_env.set("y", 30)  # Shadow parent variable

        assert child_env.parent is parent_env
        assert child_env.get("x") == 10
        assert child_env.get("y") == 30  # Shadowed value
        assert parent_env.get("y") == 20  # Original value

        # Test undefined variable
        with pytest.raises(NameError, match="Name 'undefined_var' is not defined"):
            env.get("undefined_var")


class TestSiluInterpreter:
    """Tests for the SiluInterpreter class."""

    def test_initialization_and_basic_operations(self):
        # Test initialization
        interpreter = SiluInterpreter()
        assert isinstance(interpreter.env, Environment)

        custom_env = Environment()
        interpreter_with_env = SiluInterpreter(env=custom_env)
        assert interpreter_with_env.env is custom_env

        # Test visiting modules
        empty_module = ast.Module(body=[], type_ignores=[])
        interpreter.visit(empty_module)

        tree = ast.parse("pass")
        interpreter.visit(tree)

    @pytest.mark.parametrize(
        "value,expected_type",
        [
            (42, int),
            ("hello", str),
            (3.14, float),
            (True, bool),
            (False, bool),
        ],
    )
    def test_visit_constant(self, value, expected_type):
        interpreter = SiluInterpreter()
        node = ast.Constant(value=value)
        result = interpreter.visit_Constant(node)
        assert result == value
        assert isinstance(result, expected_type)

    def test_visit_name(self):
        interpreter = SiluInterpreter()

        # Test name operations
        interpreter.env.set("x", 10)
        load_node = ast.Name(id="x", ctx=ast.Load())
        assert interpreter.visit_Name(load_node) == 10

        # Test undefined variable
        undefined_node = ast.Name(id="y", ctx=ast.Load())
        with pytest.raises(NameError, match="Name 'y' is not defined"):
            interpreter.visit_Name(undefined_node)

        # Test store context
        store_node = ast.Name(id="z", ctx=ast.Store())
        interpreter.visit_Name(store_node)

        # Test unsupported context
        unsupported_node = ast.Name(id="w", ctx=ast.Del())
        with pytest.raises(NotImplementedError, match="Unsupported name context"):
            interpreter.visit_Name(unsupported_node)

    def test_visit_assign(self):
        interpreter = SiluInterpreter()

        # Test simple assignment
        target = ast.Name(id="x", ctx=ast.Store())
        value = ast.Constant(value=42)
        assign_node = ast.Assign(targets=[target], value=value)
        interpreter.visit_Assign(assign_node)
        assert interpreter.env.get("x") == 42

        # Test assignment with expression
        interpreter.env.set("y", 10)
        target = ast.Name(id="z", ctx=ast.Store())
        left = ast.Name(id="y", ctx=ast.Load())
        right = ast.Constant(value=5)
        value = ast.BinOp(left=left, op=ast.Add(), right=right)
        assign_node = ast.Assign(targets=[target], value=value)
        interpreter.visit_Assign(assign_node)
        assert interpreter.env.get("z") == 15

        # Test multiple targets assignment
        target1 = ast.Name(id="a", ctx=ast.Store())
        target2 = ast.Name(id="b", ctx=ast.Store())
        value = ast.Constant(value=42)
        assign_node = ast.Assign(targets=[target1, target2], value=value)
        interpreter.visit_Assign(assign_node)
        assert interpreter.env.get("a") == 42
        assert interpreter.env.get("b") == 42

        # Test multiple targets with three variables
        target1 = ast.Name(id="x1", ctx=ast.Store())
        target2 = ast.Name(id="y1", ctx=ast.Store())
        target3 = ast.Name(id="z1", ctx=ast.Store())
        value = ast.Constant(value="hello")
        assign_node = ast.Assign(targets=[target1, target2, target3], value=value)
        interpreter.visit_Assign(assign_node)
        assert interpreter.env.get("x1") == "hello"
        assert interpreter.env.get("y1") == "hello"
        assert interpreter.env.get("z1") == "hello"

    def test_subscript_operations(self):
        """Test subscript assignment and access operations."""
        interpreter = SiluInterpreter()

        # Dictionary subscript assignment
        interpreter.env.set("d", {})
        target = ast.Subscript(
            value=ast.Name(id="d", ctx=ast.Load()),
            slice=ast.Constant(value="key"),
            ctx=ast.Store(),
        )
        value = ast.Constant(value="value")
        assign_node = ast.Assign(targets=[target], value=value)
        interpreter.visit_Assign(assign_node)
        assert interpreter.env.get("d")["key"] == "value"

        # List subscript assignment and access
        interpreter.env.set("lst", [1, 2, 3])
        target = ast.Subscript(
            value=ast.Name(id="lst", ctx=ast.Load()),
            slice=ast.Constant(value=1),
            ctx=ast.Store(),
        )
        assign_node = ast.Assign(targets=[target], value=ast.Constant(value=99))
        interpreter.visit_Assign(assign_node)
        assert interpreter.env.get("lst")[1] == 99

        # Test subscript access
        subscript_node = ast.Subscript(
            value=ast.Name(id="lst", ctx=ast.Load()),
            slice=ast.Constant(value=0),
            ctx=ast.Load(),
        )
        assert interpreter.visit_Subscript(subscript_node) == 1

        # Test negative indexing
        subscript_node = ast.Subscript(
            value=ast.Name(id="lst", ctx=ast.Load()),
            slice=ast.Constant(value=-1),
            ctx=ast.Load(),
        )
        assert interpreter.visit_Subscript(subscript_node) == 3

        # Test list index errors
        target = ast.Subscript(
            value=ast.Name(id="lst", ctx=ast.Load()),
            slice=ast.Constant(value="invalid"),
            ctx=ast.Store(),
        )
        assign_node = ast.Assign(targets=[target], value=ast.Constant(value=99))
        with pytest.raises(TypeError, match="list indices must be integers"):
            interpreter.visit_Assign(assign_node)

        target = ast.Subscript(
            value=ast.Name(id="lst", ctx=ast.Load()),
            slice=ast.Constant(value=10),
            ctx=ast.Store(),
        )
        assign_node = ast.Assign(targets=[target], value=ast.Constant(value=99))
        with pytest.raises(IndexError, match="list index out of range"):
            interpreter.visit_Assign(assign_node)

        # Test unsupported subscript assignment
        interpreter.env.set("x", 42)
        target = ast.Subscript(
            value=ast.Name(id="x", ctx=ast.Load()),
            slice=ast.Constant(value=0),
            ctx=ast.Store(),
        )
        assign_node = ast.Assign(targets=[target], value=ast.Constant(value=99))
        with pytest.raises(
            TypeError, match="'int' object does not support item assignment"
        ):
            interpreter.visit_Assign(assign_node)

    @pytest.mark.parametrize(
        "op,expected",
        [
            (ast.Add(), 8),
            (ast.Sub(), 2),
            (ast.Mult(), 15),
            (ast.Div(), 1.6666666666666667),
            (ast.FloorDiv(), 1),
            (ast.Mod(), 2),
            (ast.Pow(), 125),
        ],
    )
    def test_visit_binop_normal(self, op, expected):
        interpreter = SiluInterpreter()
        left = ast.Constant(value=5)
        right = ast.Constant(value=3)
        node = ast.BinOp(left=left, op=op, right=right)
        assert interpreter.visit_BinOp(node) == expected

    @pytest.mark.parametrize(
        "op,error_msg",
        [
            (ast.Div(), "Division by zero"),
            (ast.Mod(), "Modulo by zero"),
            (ast.FloorDiv(), "Division by zero"),
        ],
    )
    def test_visit_binop_division_by_zero(self, op, error_msg):
        interpreter = SiluInterpreter()
        left = ast.Constant(value=5)
        right = ast.Constant(value=0)
        node = ast.BinOp(left=left, op=op, right=right)
        with pytest.raises(ZeroDivisionError, match=error_msg):
            interpreter.visit_BinOp(node)

    def test_visit_binop_unsupported(self):
        interpreter = SiluInterpreter()
        left = ast.Constant(value=5)
        right = ast.Constant(value=3)
        node = ast.BinOp(left=left, op=ast.LShift(), right=right)
        with pytest.raises(NotImplementedError, match="Unsupported operator: LShift"):
            interpreter.visit_BinOp(node)

    @pytest.mark.parametrize(
        "op,operand,expected",
        [
            (ast.UAdd(), 5, 5),
            (ast.USub(), 5, -5),
            (ast.Not(), True, False),
            (ast.Not(), False, True),
        ],
    )
    def test_visit_unaryop(self, op, operand, expected):
        interpreter = SiluInterpreter()
        node = ast.UnaryOp(op=op, operand=ast.Constant(value=operand))
        result = interpreter.visit_UnaryOp(node)
        assert result == expected

    def test_visit_unaryop_unsupported(self):
        interpreter = SiluInterpreter()
        operand = ast.Constant(value=5)
        node = ast.UnaryOp(op=ast.Invert(), operand=operand)
        with pytest.raises(NotImplementedError, match="Unsupported operator: Invert"):
            interpreter.visit_UnaryOp(node)

    @pytest.mark.parametrize(
        "values,op,expected",
        [
            ([ast.Constant(value=True), ast.Constant(value=False)], ast.And(), False),
            ([ast.Constant(value=True), ast.Constant(value=True)], ast.And(), True),
            ([ast.Constant(value=False), ast.Constant(value=True)], ast.Or(), True),
            ([ast.Constant(value=False), ast.Constant(value=False)], ast.Or(), False),
        ],
    )
    def test_visit_boolop(self, values, op, expected):
        interpreter = SiluInterpreter()
        node = ast.BoolOp(op=op, values=values)
        assert interpreter.visit_BoolOp(node) == expected

    def test_visit_boolop_with_variables(self):
        interpreter = SiluInterpreter()
        interpreter.env.set("a", True)
        interpreter.env.set("b", False)
        values = [ast.Name(id="a", ctx=ast.Load()), ast.Name(id="b", ctx=ast.Load())]
        node = ast.BoolOp(op=ast.And(), values=values)
        assert not interpreter.visit_BoolOp(node)

    def test_visit_boolop_unsupported(self):
        interpreter = SiluInterpreter()
        values = [ast.Constant(value=True), ast.Constant(value=False)]
        node = ast.BoolOp(op=ast.MatMult(), values=values)
        with pytest.raises(NotImplementedError, match="Unsupported operator: MatMult"):
            interpreter.visit_BoolOp(node)

    def test_visit_compare_basic(self):
        interpreter = SiluInterpreter()
        left = ast.Constant(value=5)
        ops = [ast.Eq()]
        comparators = [ast.Constant(value=5)]
        node = ast.Compare(left=left, ops=ops, comparators=comparators)
        assert interpreter.visit_Compare(node) is True

    def test_visit_compare_chained(self):
        interpreter = SiluInterpreter()
        # Test 3 < 5 < 7 (should be True)
        left = ast.Constant(value=3)
        ops = [ast.Lt(), ast.Lt()]
        comparators = [ast.Constant(value=5), ast.Constant(value=7)]
        node = ast.Compare(left=left, ops=ops, comparators=comparators)
        assert interpreter.visit_Compare(node) is True

        # Test 3 < 5 < 4 (should be False)
        ops = [ast.Lt(), ast.Lt()]
        comparators = [ast.Constant(value=5), ast.Constant(value=4)]
        node = ast.Compare(left=left, ops=ops, comparators=comparators)
        assert interpreter.visit_Compare(node) is False

    def test_visit_compare_errors(self):
        interpreter = SiluInterpreter()
        left = ast.Constant(value=5)
        ops = [ast.BitAnd()]  # Unsupported operator
        comparators = [ast.Constant(value=3)]
        node = ast.Compare(left=left, ops=ops, comparators=comparators)
        with pytest.raises(NotImplementedError, match="Unsupported operator: BitAnd"):
            interpreter.visit_Compare(node)

        # Test division by zero in comparison
        left = ast.Constant(value=1)
        ops = [ast.Lt()]
        comparators = [
            ast.BinOp(
                left=ast.Constant(value=5), op=ast.Div(), right=ast.Constant(value=0)
            )
        ]
        node = ast.Compare(left=left, ops=ops, comparators=comparators)
        with pytest.raises(ZeroDivisionError, match="Division by zero"):
            interpreter.visit_Compare(node)

    def test_visit_expr(self):
        interpreter = SiluInterpreter()
        value_node = ast.Constant(value=42)
        expr_node = ast.Expr(value=value_node)
        result = interpreter.visit_Expr(expr_node)
        assert result == 42

    def test_control_flow_if(self):
        interpreter = SiluInterpreter()

        # Test simple if statement
        interpreter.env.set("result", 0)
        condition = ast.Constant(value=True)
        body = [
            ast.Assign(
                targets=[ast.Name(id="result", ctx=ast.Store())],
                value=ast.Constant(value=42),
            )
        ]
        if_node = ast.If(test=condition, body=body, orelse=[])
        interpreter.visit_If(if_node)
        assert interpreter.env.get("result") == 42

        # Test if-else
        condition = ast.Constant(value=False)
        orelse = [
            ast.Assign(
                targets=[ast.Name(id="result", ctx=ast.Store())],
                value=ast.Constant(value=99),
            )
        ]
        if_node = ast.If(test=condition, body=body, orelse=orelse)
        interpreter.visit_If(if_node)
        assert interpreter.env.get("result") == 99

    def test_control_flow_while(self):
        interpreter = SiluInterpreter()

        # Test while loop
        code = "i = 0\nwhile i < 3:\n    i = i + 1"
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("i") == 3

        # Test while with break
        code2 = """
i = 0
while True:
    if i >= 2:
        break
    i = i + 1
        """
        interpreter2 = SiluInterpreter()
        tree2 = ast.parse(code2)
        interpreter2.visit(tree2)
        assert interpreter2.env.get("i") == 2

    @pytest.mark.parametrize(
        "code,var_name,expected",
        [
            ("x = 5 + 3", "x", 8),
            ("y = 2 * 4", "y", 8),
            ("z = 10 / 2", "z", 5.0),
        ],
    )
    def test_e2e_programs_basic(self, code, var_name, expected):
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get(var_name) == expected

    def test_e2e_variable_usage(self):
        interpreter = SiluInterpreter()
        tree = ast.parse("a = 10\nb = 5\nc = a + b")
        interpreter.visit(tree)
        assert interpreter.env.get("c") == 15

    def test_builtins_available(self):
        interpreter = SiluInterpreter()
        builtins = ["print", "type", "isinstance", "int", "float", "str", "bool"]
        type_objects = ["int_type", "float_type", "str_type", "bool_type"]

        for builtin in builtins:
            assert builtin in interpreter.env.vars
            assert callable(interpreter.env.vars[builtin])

        for type_obj in type_objects:
            assert type_obj in interpreter.env.vars

    def test_list_function(self):
        interpreter = SiluInterpreter()
        assert interpreter.env.vars["list"]() == []
        assert interpreter.env.vars["list"]([1, 2, 3]) == [1, 2, 3]
        assert interpreter.env.vars["list"]("hello") == ["h", "e", "l", "l", "o"]

    def test_print_function(self):
        interpreter = SiluInterpreter()
        # Just test that print function is callable (output testing is complex)
        interpreter.env.vars["print"]("test")

    def test_visit_call_method(self):
        """Test method calls like list.append."""
        interpreter = SiluInterpreter()
        interpreter.env.set("lst", [1, 2, 3])

        call_node = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="lst", ctx=ast.Load()), attr="append", ctx=ast.Load()
            ),
            args=[ast.Constant(value=4)],
            keywords=[],
        )
        interpreter.visit_Call(call_node)
        assert interpreter.env.get("lst") == [1, 2, 3, 4]

    def test_type_function(self):
        interpreter = SiluInterpreter()
        assert interpreter.env.vars["type"](42) is int
        assert interpreter.env.vars["type"](3.14) is float
        assert interpreter.env.vars["type"]("hello") is str
        assert interpreter.env.vars["type"](True) is bool

    @pytest.mark.parametrize(
        "func_name,input_val,expected",
        [
            ("int", 3.14, 3),
            ("int", "42", 42),
            ("int", True, 1),
            ("int", None, 0),
            ("float", 42, 42.0),
            ("float", "3.14", 3.14),
            ("float", True, 1.0),
            ("float", None, 0.0),
            ("str", 42, "42"),
            ("str", 3.14, "3.14"),
            ("str", True, "True"),
            ("str", None, ""),
            ("bool", 1, True),
            ("bool", 0, False),
            ("bool", "hello", True),
            ("bool", None, False),
        ],
    )
    def test_conversion_functions(self, func_name, input_val, expected):
        interpreter = SiluInterpreter()
        if input_val is None:
            assert interpreter.env.vars[func_name]() == expected
        else:
            assert interpreter.env.vars[func_name](input_val) == expected

    @pytest.mark.parametrize(
        "value,type_cls,expected",
        [
            (42, int, True),
            (3.14, float, True),
            ("hello", str, True),
            (True, bool, True),
            (42, float, False),
            (3.14, int, False),
            ("hello", bool, False),
            (True, str, False),
        ],
    )
    def test_isinstance_function(self, value, type_cls, expected):
        interpreter = SiluInterpreter()
        assert interpreter.env.vars["isinstance"](value, type_cls) == expected

    def test_isinstance_with_type_objects(self):
        interpreter = SiluInterpreter()
        test_cases = [
            (42, "int_type"),
            (3.14, "float_type"),
            ("hello", "str_type"),
            (True, "bool_type"),
        ]

        for value, type_name in test_cases:
            assert interpreter.env.vars["isinstance"](
                value, interpreter.env.vars[type_name]
            )

    def test_isinstance_error_cases(self):
        interpreter = SiluInterpreter()

        # Test isinstance with list type
        assert not interpreter.env.vars["isinstance"](42, list)

        # Test isinstance with custom object that has __name__ attribute
        class CustomType:
            def __init__(self, name):
                self.__name__ = name

        custom_types = [
            (42, CustomType("int")),
            (3.14, CustomType("float")),
            ("hello", CustomType("str")),
            (True, CustomType("bool")),
        ]

        for value, custom_type in custom_types:
            assert interpreter.env.vars["isinstance"](value, custom_type)

        # Test isinstance with unknown type returns False
        assert not interpreter.env.vars["isinstance"](42, CustomType("unknown"))

    def test_builtins_error_cases(self):
        interpreter = SiluInterpreter()

        # Test int conversion errors
        with pytest.raises(ValueError):
            interpreter.env.vars["int"]("invalid")

        # Test float conversion errors
        with pytest.raises(ValueError):
            interpreter.env.vars["float"]("invalid")

        # Test isinstance with unsupported type
        class UnsupportedType:
            pass

        # This should not raise an error, just return False
        assert not interpreter.env.vars["isinstance"](42, UnsupportedType())

        # Test isinstance with custom type that has wrong __name__
        class CustomType:
            def __init__(self):
                self.__name__ = 123  # Not a string

        assert not interpreter.env.vars["isinstance"](42, CustomType())

    def test_function_definition_and_calls(self):
        """Test function definition and calling."""
        interpreter = SiluInterpreter()

        # Define and call a simple function
        code = """
def add(a, b):
    return a + b

result = add(3, 5)
        """
        tree = ast.parse(code)
        interpreter.visit(tree)

        assert "add" in interpreter.env.vars
        assert isinstance(interpreter.env.vars["add"], Function)
        assert interpreter.env.get("result") == 8

        # Test function without return (should return None)
        code2 = """
def greet(name):
    x = "Hello, " + name

result2 = greet("World")
        """
        tree2 = ast.parse(code2)
        interpreter.visit(tree2)
        assert interpreter.env.get("result2") is None

    def test_visit_return(self):
        interpreter = SiluInterpreter()
        return_node = ast.Return(value=ast.Constant(value=42))
        with pytest.raises(ReturnException) as exc_info:
            interpreter.visit_Return(return_node)
        assert exc_info.value.value == 42


def test_main_function():
    """Test that main function exists."""
    from silu.cli import main

    assert main is not None


def test_module_execution():
    """Test module-level execution."""
    interpreter = SiluInterpreter()
    code = """
a = 10
b = 5
c = a + b
    """
    tree = ast.parse(code)
    interpreter.visit(tree)
    assert interpreter.env.get("a") == 10
    assert interpreter.env.get("b") == 5
    assert interpreter.env.get("c") == 15


class TestElifForSupport:
    """Test elif and for loop support."""

    def test_elif_support(self):
        """Test elif clause support."""
        interpreter = SiluInterpreter()
        code = """
x = 2
if x == 1:
    result = "one"
elif x == 2:
    result = "two"
else:
    result = "other"
        """
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == "two"

    def test_for_loop_support(self):
        """Test for loop with list and range."""
        interpreter = SiluInterpreter()

        # For loop with list
        code = """
total = 0
for item in [1, 2, 3]:
    total = total + item
        """
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("total") == 6

    def test_for_loop_with_range(self):
        """Test for loop with range function."""
        interpreter = SiluInterpreter()
        code = """
count = 0
for i in range(3):
    count = count + 1
        """
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("count") == 3

    def test_nested_control_flow(self):
        """Test nested control structures."""
        interpreter = SiluInterpreter()
        code = """
result = 0
for i in range(3):
    if i % 2 == 0:
        result = result + i
        """
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 2  # 0 + 2

    def test_append_method_error(self):
        """Test error handling for unsupported append operations."""
        interpreter = SiluInterpreter()
        interpreter.env.set("x", 42)  # Not a list

        call_node = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="x", ctx=ast.Load()), attr="append", ctx=ast.Load()
            ),
            args=[ast.Constant(value=1)],
            keywords=[],
        )
        with pytest.raises(AttributeError):
            interpreter.visit_Call(call_node)

    def test_visit_call_append_error(self):
        """Test append method call error handling."""
        interpreter = SiluInterpreter()
        interpreter.env.set("my_string", "hello")

        call_node = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="my_string", ctx=ast.Load()),
                attr="append",
                ctx=ast.Load(),
            ),
            args=[ast.Constant(value="world")],
            keywords=[],
        )
        with pytest.raises(AttributeError):
            interpreter.visit_Call(call_node)

    def test_for_else_clause(self):
        """Test for loop with else clause."""
        interpreter = SiluInterpreter()
        code = """
result = "not found"
for i in range(3):
    if i == 5:  # This will never be true
        result = "found"
        break
else:
    result = "completed"
        """
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == "completed"

    @pytest.mark.skip(reason="Complex tuple unpacking not yet implemented")
    def test_for_loop_unsupported_target(self):
        """Test for loop with unsupported target types."""
        interpreter = SiluInterpreter()

        # Create a for loop with tuple target (unsupported)
        target = ast.Tuple(
            elts=[ast.Name(id="a", ctx=ast.Store()), ast.Name(id="b", ctx=ast.Store())],
            ctx=ast.Store(),
        )
        for_node = ast.For(
            target=target,
            iter=ast.List(elts=[ast.Constant(value=1)], ctx=ast.Load()),
            body=[ast.Pass()],
            orelse=[],
        )
        with pytest.raises(
            NotImplementedError,
            match="Only simple variable targets are supported in for loops",
        ):
            interpreter.visit_For(for_node)


class TestAugmentedAssignment:
    """Tests for augmented assignment operations (+=, -=, etc.)."""

    def test_aug_assign_addition(self):
        """Test += operator."""
        code = """
x = 10
x += 5
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("x") == 15

    def test_aug_assign_subtraction(self):
        """Test -= operator."""
        code = """
y = 20
y -= 8
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("y") == 12

    def test_aug_assign_multiplication(self):
        """Test *= operator."""
        code = """
z = 3
z *= 4
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("z") == 12

    def test_aug_assign_division(self):
        """Test /= operator."""
        code = """
w = 20
w /= 4
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("w") == 5.0

    def test_aug_assign_floor_division(self):
        """Test //= operator."""
        code = """
a = 17
a //= 3
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 5

    def test_aug_assign_modulo(self):
        """Test %= operator."""
        code = """
b = 17
b %= 5
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("b") == 2

    def test_aug_assign_power(self):
        """Test **= operator."""
        code = """
c = 2
c **= 3
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("c") == 8

    def test_aug_assign_in_while_loop(self):
        """Test augmented assignment in while loop (original bug case)."""
        code = """
def countdown(n):
    while n > 0:
        n -= 1
    return n

result = countdown(3)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 0

    def test_aug_assign_list_element(self):
        """Test augmented assignment on list elements."""
        code = """
numbers = [1, 2, 3]
numbers[0] += 10
numbers[1] *= 5
numbers[2] -= 1
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        numbers = interpreter.env.get("numbers")
        assert numbers == [11, 10, 2]

    def test_aug_assign_nested_loops(self):
        """Test augmented assignment in nested loops."""
        code = """
total = 0
for i in [1, 2, 3]:
    j = 2
    while j > 0:
        total += i
        j -= 1
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("total") == 12  # (1+1) + (2+2) + (3+3) = 12

    def test_aug_assign_with_function_call(self):
        """Test augmented assignment with function call as value."""
        code = """
def get_value():
    return 5

x = 10
x += get_value()
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("x") == 15

    def test_aug_assign_variable_not_defined(self):
        """Test augmented assignment on undefined variable."""
        code = """
undefined_var += 5
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(NameError, match="Name 'undefined_var' is not defined"):
            interpreter.visit(tree)


class TestTupleUnpacking:
    """Tests for tuple unpacking assignment operations."""

    def test_basic_tuple_unpacking(self):
        """Test basic tuple unpacking assignment."""
        code = """
a, b = 1, 2
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 1
        assert interpreter.env.get("b") == 2

    def test_variable_swap(self):
        """Test variable swapping with tuple unpacking."""
        code = """
x = 10
y = 20
x, y = y, x
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("x") == 20
        assert interpreter.env.get("y") == 10

    def test_list_unpacking(self):
        """Test unpacking from a list."""
        code = """
nums = [100, 200, 300]
a, b, c = nums
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 100
        assert interpreter.env.get("b") == 200
        assert interpreter.env.get("c") == 300

    def test_string_unpacking(self):
        """Test unpacking from a string."""
        code = """
s = "hi"
c1, c2 = s
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("c1") == "h"
        assert interpreter.env.get("c2") == "i"

    def test_tuple_unpacking_too_many_values(self):
        """Test error when too many values to unpack."""
        code = """
a, b = 1, 2, 3
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(
            ValueError, match="too many values to unpack \\(expected 2\\)"
        ):
            interpreter.visit(tree)

    def test_tuple_unpacking_not_enough_values(self):
        """Test error when not enough values to unpack."""
        code = """
a, b, c = 1, 2
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(
            ValueError, match="not enough values to unpack \\(expected 3, got 2\\)"
        ):
            interpreter.visit(tree)

    def test_tuple_unpacking_non_sequence(self):
        """Test error when trying to unpack a non-sequence."""
        code = """
a, b = 42
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(TypeError, match="cannot unpack non-sequence int"):
            interpreter.visit(tree)

    def test_nested_function_with_tuple_unpacking(self):
        """Test tuple unpacking inside function calls."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b

result = fibonacci(5)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 5

    def test_tuple_unpacking_with_expression(self):
        """Test tuple unpacking with expressions on right side."""
        code = """
x = 10
y = 20
a, b = x + 5, y * 2
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 15
        assert interpreter.env.get("b") == 40

    def test_tuple_unpacking_in_for_loop(self):
        """Test tuple unpacking already supported in for loops."""
        code = """
pairs = [(1, 2), (3, 4), (5, 6)]
result = []
for a, b in pairs:
    result.append(a + b)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        result = interpreter.env.get("result")
        assert result == [3, 7, 11]


class TestMultipleTargetAssignment:
    """Tests for multiple target assignment operations (a = b = c = value)."""

    def test_simple_multiple_assignment(self):
        """Test basic multiple target assignment with two variables."""
        code = """
a = b = 42
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 42
        assert interpreter.env.get("b") == 42

    def test_three_target_assignment(self):
        """Test multiple target assignment with three variables."""
        code = """
x = y = z = "hello"
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("x") == "hello"
        assert interpreter.env.get("y") == "hello"
        assert interpreter.env.get("z") == "hello"

    def test_many_target_assignment(self):
        """Test assignment with many targets."""
        code = """
a = b = c = d = e = f = 123
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 123
        assert interpreter.env.get("b") == 123
        assert interpreter.env.get("c") == 123
        assert interpreter.env.get("d") == 123
        assert interpreter.env.get("e") == 123
        assert interpreter.env.get("f") == 123

    def test_multiple_assignment_with_expression(self):
        """Test multiple assignment with complex expression."""
        code = """
base = 10
x = y = z = base * 2 + 5
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("x") == 25
        assert interpreter.env.get("y") == 25
        assert interpreter.env.get("z") == 25

    def test_multiple_assignment_independence(self):
        """Test that variables assigned together are independent for immutable types."""
        code = """
a = b = c = 100
a = 200
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 200
        assert interpreter.env.get("b") == 100
        assert interpreter.env.get("c") == 100

    def test_multiple_assignment_with_list(self):
        """Test multiple assignment with mutable objects (list)."""
        code = """
list1 = list2 = [1, 2, 3]
list1[0] = 999
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        list1 = interpreter.env.get("list1")
        list2 = interpreter.env.get("list2")
        assert list1 == [999, 2, 3]
        assert list2 == [999, 2, 3]  # Same reference, so both are modified

    def test_multiple_assignment_with_subscript(self):
        """Test multiple assignment combined with subscript assignment."""
        code = """
arr1 = [0, 0, 0]
arr2 = [0, 0, 0]
arr1[0] = arr2[1] = 99
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        arr1 = interpreter.env.get("arr1")
        arr2 = interpreter.env.get("arr2")
        assert arr1 == [99, 0, 0]
        assert arr2 == [0, 99, 0]

    def test_multiple_assignment_with_tuple_unpacking(self):
        """Test multiple assignment combined with tuple unpacking."""
        code = """
a, b = c, d = [10, 20]
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("a") == 10
        assert interpreter.env.get("b") == 20
        assert interpreter.env.get("c") == 10
        assert interpreter.env.get("d") == 20

    def test_mixed_simple_and_tuple_assignment(self):
        """Test mixing simple and tuple assignment targets."""
        code = """
x = y, z = [100, 200]
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("x") == [100, 200]
        assert interpreter.env.get("y") == 100
        assert interpreter.env.get("z") == 200

    def test_multiple_assignment_different_types(self):
        """Test multiple assignment with different data types."""
        code = """
# Numbers
num1 = num2 = 42

# Strings
str1 = str2 = "test"

# Lists
list1 = list2 = [1, 2, 3]

# Booleans
bool1 = bool2 = True
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)

        assert interpreter.env.get("num1") == 42
        assert interpreter.env.get("num2") == 42
        assert interpreter.env.get("str1") == "test"
        assert interpreter.env.get("str2") == "test"
        assert interpreter.env.get("list1") == [1, 2, 3]
        assert interpreter.env.get("list2") == [1, 2, 3]
        assert interpreter.env.get("bool1") is True
        assert interpreter.env.get("bool2") is True

    def test_multiple_assignment_in_function(self):
        """Test multiple assignment inside a function."""
        code = """
def test_func():
    a = b = c = 42
    return a + b + c

result = test_func()
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 126
