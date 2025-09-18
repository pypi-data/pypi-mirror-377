"""
Unit tests for the Silu IR generator module.
"""

import ast
from silu.ir_generator import SiluIRGenerator


class TestSiluIRGenerator:
    """Tests for the SiluIRGenerator class."""

    def test_process_name_load(self):
        """Test processing a name with load context."""
        generator = SiluIRGenerator()
        result = generator.process_name("x", ast.Load())
        expected = ("name", "x")
        assert result == expected

    def test_process_name_store(self):
        """Test processing a name with store context."""
        generator = SiluIRGenerator()
        result = generator.process_name("x", ast.Store())
        expected = ("name", "x")
        assert result == expected

    def test_process_name_unsupported_context(self):
        """Test processing a name with unsupported context."""
        generator = SiluIRGenerator()
        # Current implementation doesn't validate context, just returns name
        result = generator.process_name("x", ast.Del())
        assert result == ("name", "x")

    def test_process_operation_binary(self):
        """Test processing binary operations."""
        generator = SiluIRGenerator()

        # Test addition
        result = generator.process_operation("+", 5, 3)
        expected = ("+", 5, 3)
        assert result == expected

        # Test multiplication
        result = generator.process_operation("*", 4, 6)
        expected = ("*", 4, 6)
        assert result == expected

    def test_process_operation_unary(self):
        """Test processing unary operations."""
        generator = SiluIRGenerator()

        # Test unary minus
        result = generator.process_operation("-", 5)
        expected = ("-", 5)
        assert result == expected

        # Test not operation
        result = generator.process_operation("not", True)
        expected = ("not", True)
        assert result == expected

    def test_visit_module(self):
        """Test visiting a module."""
        generator = SiluIRGenerator()

        # Create a module with an assignment
        assign_target = ast.Name(id="x", ctx=ast.Store())
        assign_value = ast.Constant(value=42)
        assign_node = ast.Assign(targets=[assign_target], value=assign_value)
        module = ast.Module(body=[assign_node], type_ignores=[])

        result = generator.visit_Module(module)
        assert isinstance(result, tuple)
        assert result[0] == "module"
        assert len(result[1]) == 1

    def test_visit_assign(self):
        """Test visiting an assignment."""
        generator = SiluIRGenerator()

        # Create an assignment
        target = ast.Name(id="x", ctx=ast.Store())
        value = ast.Constant(value=42)
        assign = ast.Assign(targets=[target], value=value)

        result = generator.visit_Assign(assign)
        expected = ("assign", "x", ("const", 42), None)
        assert result == expected

    def test_visit_binop(self):
        """Test visiting binary operations."""
        generator = SiluIRGenerator()

        # Create a binary operation
        left = ast.Constant(value=5)
        right = ast.Constant(value=3)
        binop = ast.BinOp(left=left, op=ast.Add(), right=right)

        result = generator.visit_BinOp(binop)
        expected = ("+", ("const", 5), ("const", 3))
        assert result == expected

    def test_visit_unaryop(self):
        """Test visiting unary operations."""
        generator = SiluIRGenerator()

        # Create a unary operation
        operand = ast.Constant(value=5)
        unaryop = ast.UnaryOp(op=ast.USub(), operand=operand)

        result = generator.visit_UnaryOp(unaryop)
        expected = ("-", ("const", 5))
        assert result == expected

    def test_visit_compare(self):
        """Test visiting comparisons."""
        generator = SiluIRGenerator()

        # Create a comparison
        left = ast.Constant(value=5)
        comparators = [ast.Constant(value=3)]
        ops = [ast.Lt()]
        compare = ast.Compare(left=left, ops=ops, comparators=comparators)

        result = generator.visit_Compare(compare)
        expected = ("<", ("const", 5), ("const", 3))
        assert result == expected

    def test_visit_boolop(self):
        """Test visiting boolean operations."""
        generator = SiluIRGenerator()

        # Create a boolean operation
        values = [ast.Constant(value=True), ast.Constant(value=False)]
        boolop = ast.BoolOp(op=ast.And(), values=values)

        result = generator.visit_BoolOp(boolop)
        expected = ("and", ("const", True), ("const", False))
        assert result == expected

    def test_visit_name(self):
        """Test visiting names."""
        generator = SiluIRGenerator()

        # Test load context
        name_load = ast.Name(id="x", ctx=ast.Load())
        result = generator.visit_Name(name_load)
        expected = ("name", "x")
        assert result == expected

        # Test store context
        name_store = ast.Name(id="y", ctx=ast.Store())
        result = generator.visit_Name(name_store)
        expected = ("name", "y")
        assert result == expected

    def test_visit_constant(self):
        """Test visiting constants."""
        generator = SiluIRGenerator()

        # Test integer constant
        const_int = ast.Constant(value=42)
        assert generator.visit_Constant(const_int) == ("const", 42)

        # Test string constant
        const_str = ast.Constant(value="hello")
        assert generator.visit_Constant(const_str) == ("const", "hello")

        # Test boolean constant
        const_bool = ast.Constant(value=True)
        assert generator.visit_Constant(const_bool) == ("const", True)

        # Test float constant
        const_float = ast.Constant(value=3.14)
        assert generator.visit_Constant(const_float) == ("const", 3.14)

    def test_visit_expr(self):
        """Test visiting expressions."""
        generator = SiluIRGenerator()

        # Create an expression
        value = ast.Constant(value=42)
        expr = ast.Expr(value=value)

        result = generator.visit_Expr(expr)
        assert result == ("const", 42)

    def test_complex_expression(self):
        """Test visiting a complex expression."""
        generator = SiluIRGenerator()

        # Create: x = 10 + 5 * 2
        left = ast.Constant(value=10)
        mult_left = ast.Constant(value=5)
        mult_right = ast.Constant(value=2)
        mult = ast.BinOp(left=mult_left, op=ast.Mult(), right=mult_right)
        add = ast.BinOp(left=left, op=ast.Add(), right=mult)

        target = ast.Name(id="x", ctx=ast.Store())
        assign = ast.Assign(targets=[target], value=add)

        result = generator.visit_Assign(assign)
        expected = (
            "assign",
            "x",
            ("+", ("const", 10), ("*", ("const", 5), ("const", 2))),
            None,
        )
        assert result == expected

    def test_chained_comparison(self):
        """Test visiting chained comparisons."""
        generator = SiluIRGenerator()

        # Create: 1 < x < 10
        left = ast.Constant(value=1)
        comparators = [ast.Name(id="x", ctx=ast.Load()), ast.Constant(value=10)]
        ops = [ast.Lt(), ast.Lt()]
        compare = ast.Compare(left=left, ops=ops, comparators=comparators)

        result = generator.visit_Compare(compare)
        expected = (
            "chained_compare",
            (("<", ("const", 1), ("name", "x")), ("<", ("name", "x"), ("const", 10))),
        )
        assert result == expected

    def test_nested_operations(self):
        """Test visiting nested operations."""
        generator = SiluIRGenerator()

        # Create: (a + b) * (c - d)
        # Left side: a + b
        left_a = ast.Name(id="a", ctx=ast.Load())
        left_b = ast.Name(id="b", ctx=ast.Load())
        left_add = ast.BinOp(left=left_a, op=ast.Add(), right=left_b)

        # Right side: c - d
        right_c = ast.Name(id="c", ctx=ast.Load())
        right_d = ast.Name(id="d", ctx=ast.Load())
        right_sub = ast.BinOp(left=right_c, op=ast.Sub(), right=right_d)

        # Multiply them
        mult = ast.BinOp(left=left_add, op=ast.Mult(), right=right_sub)

        result = generator.visit_BinOp(mult)
        expected = (
            "*",
            ("+", ("name", "a"), ("name", "b")),
            ("-", ("name", "c"), ("name", "d")),
        )
        assert result == expected

    def test_subscript_assign(self):
        """Test subscript assignment operations."""
        generator = SiluIRGenerator()

        # Test dictionary subscript assignment: d["key"] = "value"
        target = ast.Subscript(
            value=ast.Name(id="d", ctx=ast.Load()),
            slice=ast.Constant(value="key"),
            ctx=ast.Store(),
        )
        value = ast.Constant(value="value")
        assign_node = ast.Assign(targets=[target], value=value)

        result = generator.visit_Assign(assign_node)
        expected = (
            "subscript_assign",
            ("name", "d"),
            ("const", "key"),
            ("const", "value"),
        )
        assert result == expected

        # Test list subscript assignment: arr[1] = 99
        target = ast.Subscript(
            value=ast.Name(id="arr", ctx=ast.Load()),
            slice=ast.Constant(value=1),
            ctx=ast.Store(),
        )
        value = ast.Constant(value=99)
        assign_node = ast.Assign(targets=[target], value=value)

        result = generator.visit_Assign(assign_node)
        expected = ("subscript_assign", ("name", "arr"), ("const", 1), ("const", 99))
        assert result == expected


class TestMultipleTargetAssignmentIR:
    """Tests for multiple target assignment IR generation."""

    def test_simple_multiple_assignment(self):
        """Test IR generation for simple multiple assignment: a = b = 1"""
        generator = SiluIRGenerator()

        target1 = ast.Name(id="a", ctx=ast.Store())
        target2 = ast.Name(id="b", ctx=ast.Store())
        value = ast.Constant(value=1)
        assign_node = ast.Assign(targets=[target1, target2], value=value)

        result = generator.visit_Assign(assign_node)
        expected = (
            "multi_assign",
            (("assign", "a", ("const", 1), None), ("assign", "b", ("const", 1), None)),
        )
        assert result == expected

    def test_three_target_assignment(self):
        """Test IR generation for three target assignment: x = y = z = 'hello'"""
        generator = SiluIRGenerator()

        target1 = ast.Name(id="x", ctx=ast.Store())
        target2 = ast.Name(id="y", ctx=ast.Store())
        target3 = ast.Name(id="z", ctx=ast.Store())
        value = ast.Constant(value="hello")
        assign_node = ast.Assign(targets=[target1, target2, target3], value=value)

        result = generator.visit_Assign(assign_node)
        expected = (
            "multi_assign",
            (
                ("assign", "x", ("const", "hello"), None),
                ("assign", "y", ("const", "hello"), None),
                ("assign", "z", ("const", "hello"), None),
            ),
        )
        assert result == expected

    def test_multiple_assignment_with_expression(self):
        """Test IR generation for multiple assignment with expression: a = b = 2 + 3"""
        generator = SiluIRGenerator()

        target1 = ast.Name(id="a", ctx=ast.Store())
        target2 = ast.Name(id="b", ctx=ast.Store())
        left = ast.Constant(value=2)
        right = ast.Constant(value=3)
        value = ast.BinOp(left=left, op=ast.Add(), right=right)
        assign_node = ast.Assign(targets=[target1, target2], value=value)

        result = generator.visit_Assign(assign_node)
        expected = (
            "multi_assign",
            (
                ("assign", "a", ("+", ("const", 2), ("const", 3)), None),
                ("assign", "b", ("+", ("const", 2), ("const", 3)), None),
            ),
        )
        assert result == expected

    def test_multiple_assignment_with_subscript(self):
        """Test IR generation for multiple assignment with subscript: arr1[0] = arr2[1] = 99"""
        generator = SiluIRGenerator()

        target1 = ast.Subscript(
            value=ast.Name(id="arr1", ctx=ast.Load()),
            slice=ast.Constant(value=0),
            ctx=ast.Store(),
        )
        target2 = ast.Subscript(
            value=ast.Name(id="arr2", ctx=ast.Load()),
            slice=ast.Constant(value=1),
            ctx=ast.Store(),
        )
        value = ast.Constant(value=99)
        assign_node = ast.Assign(targets=[target1, target2], value=value)

        result = generator.visit_Assign(assign_node)
        expected = (
            "multi_assign",
            (
                ("subscript_assign", ("name", "arr1"), ("const", 0), ("const", 99)),
                ("subscript_assign", ("name", "arr2"), ("const", 1), ("const", 99)),
            ),
        )
        assert result == expected

    def test_multiple_assignment_with_tuple_unpacking(self):
        """Test IR generation for multiple assignment with tuple unpacking: a, b = c, d = [1, 2]"""
        generator = SiluIRGenerator()

        target1 = ast.Tuple(
            elts=[ast.Name(id="a", ctx=ast.Store()), ast.Name(id="b", ctx=ast.Store())],
            ctx=ast.Store(),
        )
        target2 = ast.Tuple(
            elts=[ast.Name(id="c", ctx=ast.Store()), ast.Name(id="d", ctx=ast.Store())],
            ctx=ast.Store(),
        )
        value = ast.List(
            elts=[ast.Constant(value=1), ast.Constant(value=2)], ctx=ast.Load()
        )
        assign_node = ast.Assign(targets=[target1, target2], value=value)

        result = generator.visit_Assign(assign_node)
        expected = (
            "multi_assign",
            (
                ("tuple_assign", ("a", "b"), ("list", (("const", 1), ("const", 2)))),
                ("tuple_assign", ("c", "d"), ("list", (("const", 1), ("const", 2)))),
            ),
        )
        assert result == expected

    def test_mixed_simple_and_tuple_assignment(self):
        """Test IR generation for mixed assignment: x = y, z = [100, 200]"""
        generator = SiluIRGenerator()

        target1 = ast.Name(id="x", ctx=ast.Store())
        target2 = ast.Tuple(
            elts=[ast.Name(id="y", ctx=ast.Store()), ast.Name(id="z", ctx=ast.Store())],
            ctx=ast.Store(),
        )
        value = ast.List(
            elts=[ast.Constant(value=100), ast.Constant(value=200)], ctx=ast.Load()
        )
        assign_node = ast.Assign(targets=[target1, target2], value=value)

        result = generator.visit_Assign(assign_node)
        expected = (
            "multi_assign",
            (
                ("assign", "x", ("list", (("const", 100), ("const", 200))), None),
                (
                    "tuple_assign",
                    ("y", "z"),
                    ("list", (("const", 100), ("const", 200))),
                ),
            ),
        )
        assert result == expected

    def test_single_target_assignment_unchanged(self):
        """Test that single target assignment still works as before."""
        generator = SiluIRGenerator()

        target = ast.Name(id="x", ctx=ast.Store())
        value = ast.Constant(value=42)
        assign_node = ast.Assign(targets=[target], value=value)

        result = generator.visit_Assign(assign_node)
        expected = ("assign", "x", ("const", 42), None)
        assert result == expected
