"""
Tests for the IR interpreter module.
"""

import pytest
from silu.ir_interpreter import IRInterpreter, execute_ir_from_string


class TestIRInterpreter:
    """Test cases for the IR interpreter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interpreter = IRInterpreter()

    def test_basic_assignment_and_variables(self):
        """Test basic variable assignment and retrieval."""
        ir = ("module", (("assign", "x", 42, None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == 42

    def test_arithmetic_operations(self):
        """Test basic arithmetic operations."""
        # x = 10 + 5
        ir = ("module", (("assign", "x", ("+", 10, 5), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == 15

        # y = 20 - 8
        ir = ("module", (("assign", "y", ("-", 20, 8), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("y") == 12

        # z = 6 * 7
        ir = ("module", (("assign", "z", ("*", 6, 7), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("z") == 42

    def test_comparison_operations(self):
        """Test comparison operations."""
        # x = 5 > 3
        ir = ("module", (("assign", "x", (">", 5, 3), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") is True

        # y = 10 <= 5
        ir = ("module", (("assign", "y", ("<=", 10, 5), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("y") is False

    def test_unary_operations(self):
        """Test unary operations."""
        # x = -42
        ir = ("module", (("assign", "x", ("-", 42), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == -42

        # y = not True
        ir = ("module", (("assign", "y", ("not", True), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("y") is False

    def test_function_call_builtin(self):
        """Test calling built-in functions."""
        # Test print function (captured via redirect would be complex, so we just test it doesn't error)
        ir = ("module", (("call", "print", ("Hello, World!",), ()),))
        result = self.interpreter.execute_program(ir)
        # print returns None
        assert result is None

        # Test type function
        ir = ("module", (("assign", "x", ("call", "type", (42,), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") is int

    def test_function_definition_and_call(self):
        """Test user-defined functions."""
        # def add(a, b): return a + b
        # result = add(3, 5)
        ir = (
            "module",
            (
                ("func_def", "add", ("a", "b"), (("return", ("+", "a", "b")),)),
                ("assign", "result", ("call", "add", (3, 5), ()), None),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") == 8

    def test_if_statement(self):
        """Test if statements."""
        # if True: x = 10
        # else: x = 20
        ir = (
            "module",
            (
                (
                    "if",
                    True,
                    (("assign", "x", 10, None),),
                    (("assign", "x", 20, None),),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == 10

        # Test false condition
        ir = (
            "module",
            (
                (
                    "if",
                    False,
                    (("assign", "y", 10, None),),
                    (("assign", "y", 20, None),),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("y") == 20

    def test_while_loop(self):
        """Test while loops."""
        # i = 0
        # while i < 3:
        #     i = i + 1
        ir = (
            "module",
            (
                ("assign", "i", 0, None),
                (
                    "while",
                    ("<", "i", 3),
                    (("assign", "i", ("+", "i", 1), None),),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("i") == 3

    def test_for_loop(self):
        """Test for loops."""
        # total = 0
        # for i in [1, 2, 3]:
        #     total = total + i
        ir = (
            "module",
            (
                ("assign", "total", 0, None),
                (
                    "for",
                    "i",
                    ("list", (1, 2, 3)),
                    (("assign", "total", ("+", "total", "i"), None),),
                    (),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("total") == 6

    def test_for_loop_with_range(self):
        """Test for loops with range."""
        # total = 0
        # for i in range(5):
        #     total = total + i
        ir = (
            "module",
            (
                ("assign", "total", 0, None),
                (
                    "for",
                    "i",
                    ("call", "range", (5,), ()),
                    (("assign", "total", ("+", "total", "i"), None),),
                    (),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("total") == 10  # 0+1+2+3+4

    def test_list_operations(self):
        """Test list creation and indexing."""
        # lst = [1, 2, 3]
        # x = lst[1]
        ir = (
            "module",
            (
                ("assign", "lst", ("list", (1, 2, 3)), None),
                ("assign", "x", ("subscript", "lst", 1), None),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("lst") == [1, 2, 3]
        assert self.interpreter._get_variable("x") == 2

    def test_dictionary_operations(self):
        """Test dictionary creation and access."""
        # d = {"key": "value", "num": 42}
        # x = d["key"]
        ir = (
            "module",
            (
                ("assign", "d", ("dict", (("key", "value"), ("num", 42))), None),
                ("assign", "x", ("subscript", "d", "key"), None),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("d") == {"key": "value", "num": 42}
        assert self.interpreter._get_variable("x") == "value"

    def test_lambda_function(self):
        """Test lambda functions."""
        # double = lambda x: x * 2
        # result = double(5)
        ir = (
            "module",
            (
                ("assign", "double", ("lambda", ("x",), ("*", "x", 2)), None),
                ("assign", "result", ("call", "double", (5,), ()), None),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") == 10

    def test_break_continue(self):
        """Test break and continue statements."""
        # count = 0
        # for i in range(10):
        #     if i == 5:
        #         break
        #     count = count + 1
        ir = (
            "module",
            (
                ("assign", "count", 0, None),
                (
                    "for",
                    "i",
                    ("call", "range", (10,), ()),
                    (
                        (
                            "if",
                            ("==", "i", 5),
                            (("break",),),
                            (),
                        ),
                        ("assign", "count", ("+", "count", 1), None),
                    ),
                    (),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("count") == 5

    def test_augmented_assignment(self):
        """Test augmented assignment operations."""
        # x = 10
        # x += 5
        ir = (
            "module",
            (
                ("assign", "x", 10, None),
                ("aug_assign", "x", "+=", 5),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == 15

    def test_chained_comparison(self):
        """Test chained comparisons."""
        # result = 3 < 5 < 7
        ir = (
            "module",
            (
                (
                    "assign",
                    "result",
                    ("chained_compare", (("<", 3, 5), ("<", 5, 7))),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") is True

        # Test failing chained comparison
        ir = (
            "module",
            (
                (
                    "assign",
                    "result2",
                    ("chained_compare", (("<", 3, 5), ("<", 7, 5))),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result2") is False

    def test_nested_function_calls(self):
        """Test nested function calls and scoping."""
        # def outer(x):
        #     def inner(y):
        #         return x + y
        #     return inner(10)
        # result = outer(5)
        ir = (
            "module",
            (
                (
                    "func_def",
                    "outer",
                    ("x",),
                    (
                        (
                            "func_def",
                            "inner",
                            ("y",),
                            (("return", ("+", "x", "y")),),
                        ),
                        ("return", ("call", "inner", (10,), ())),
                    ),
                ),
                ("assign", "result", ("call", "outer", (5,), ()), None),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") == 15

    def test_builtin_functions(self):
        """Test various built-in functions."""
        # Test len
        ir = ("module", (("assign", "x", ("call", "len", ([1, 2, 3],), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == 3

        # Test abs
        ir = ("module", (("assign", "y", ("call", "abs", (-42,), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("y") == 42

        # Test min/max
        ir = ("module", (("assign", "z", ("call", "min", (5, 3, 8), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("z") == 3

    def test_error_handling(self):
        """Test error conditions."""
        # Test undefined variable in function call
        with pytest.raises(NameError):
            ir = ("module", (("call", "print", ("some_undefined_variable",), ()),))
            self.interpreter.execute_program(ir)

        # Test division by zero
        with pytest.raises(ZeroDivisionError):
            ir = ("module", (("assign", "x", ("/", 10, 0), None),))
            self.interpreter.execute_program(ir)

        # Test undefined function
        with pytest.raises(NameError):
            ir = ("module", (("call", "undefined_func", (), ()),))
            self.interpreter.execute_program(ir)

    def test_type_conversion_functions(self):
        """Test type conversion built-in functions."""
        # Test int conversion
        ir = ("module", (("assign", "x", ("call", "int", ("42",), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == 42

        # Test float conversion
        ir = ("module", (("assign", "y", ("call", "float", ("3.14",), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("y") == 3.14

        # Test str conversion
        ir = ("module", (("assign", "z", ("call", "str", (123,), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("z") == "123"

        # Test bool conversion
        ir = ("module", (("assign", "w", ("call", "bool", (0,), ()), None),))
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("w") is False


class TestIRExecutionFromString:
    """Test IR execution from string format."""

    def test_simple_execution(self):
        """Test executing IR from string."""
        ir_string = '("module", (("assign", "x", 42, null),))'
        execute_ir_from_string(ir_string)
        # The function doesn't return the variable values, but we can test that it doesn't error

    def test_json_format_execution(self):
        """Test executing IR from JSON string."""
        ir_json = '["module", [["assign", "x", 42, null]]]'
        execute_ir_from_string(ir_json)
        # The function doesn't return the variable values, but we can test that it doesn't error


class TestComplexPrograms:
    """Test more complex programs to ensure IR interpreter works correctly."""

    def test_factorial_function(self):
        """Test recursive factorial function."""
        # def factorial(n):
        #     if n <= 1:
        #         return 1
        #     else:
        #         return n * factorial(n - 1)
        # result = factorial(5)
        ir = (
            "module",
            (
                (
                    "func_def",
                    "factorial",
                    ("n",),
                    (
                        (
                            "if",
                            ("<=", "n", 1),
                            (("return", 1),),
                            (
                                (
                                    "return",
                                    (
                                        "*",
                                        "n",
                                        (
                                            "call",
                                            "factorial",
                                            (("-", "n", 1),),
                                            (),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                ("assign", "result", ("call", "factorial", (5,), ()), None),
            ),
        )
        interpreter = IRInterpreter()
        interpreter.execute_program(ir)
        assert interpreter._get_variable("result") == 120

    def test_fibonacci_sequence(self):
        """Test generating Fibonacci sequence."""
        # def fib(n):
        #     if n <= 1:
        #         return n
        #     return fib(n-1) + fib(n-2)
        # result = fib(7)
        ir = (
            "module",
            (
                (
                    "func_def",
                    "fib",
                    ("n",),
                    (
                        (
                            "if",
                            ("<=", "n", 1),
                            (("return", "n"),),
                            (
                                (
                                    "return",
                                    (
                                        "+",
                                        ("call", "fib", (("-", "n", 1),), ()),
                                        ("call", "fib", (("-", "n", 2),), ()),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                ("assign", "result", ("call", "fib", (7,), ()), None),
            ),
        )
        interpreter = IRInterpreter()
        interpreter.execute_program(ir)
        assert interpreter._get_variable("result") == 13

    def test_list_comprehension_simulation(self):
        """Test simulating list comprehension behavior."""
        # squares = []
        # for i in range(5):
        #     squares.append(i * i)
        ir = (
            "module",
            (
                ("assign", "squares", ("list", ()), None),
                (
                    "for",
                    "i",
                    ("call", "range", (5,), ()),
                    (
                        # Simulate list.append by creating new list with existing + new element
                        (
                            "assign",
                            "squares",
                            ("+", "squares", ("list", (("*", "i", "i"),))),
                            None,
                        ),
                    ),
                    (),
                ),
            ),
        )
        interpreter = IRInterpreter()
        interpreter.execute_program(ir)
        assert interpreter._get_variable("squares") == [0, 1, 4, 9, 16]


class TestClosureFunctionality:
    """Test closure support in IR interpreter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interpreter = IRInterpreter()

    def test_basic_closure(self):
        """Test basic closure functionality."""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "make_adder",
                    ("n",),
                    (
                        (
                            "func_def",
                            "adder",
                            ("x",),
                            (("return", ("+", ("name", "x"), ("name", "n"))),),
                        ),
                        ("return", ("name", "adder")),
                    ),
                ),
                (
                    "assign",
                    "add5",
                    ("call", ("name", "make_adder"), (("const", 5),), ()),
                    None,
                ),
                (
                    "assign",
                    "result",
                    ("call", ("name", "add5"), (("const", 3),), ()),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") == 8

    def test_multiple_closures(self):
        """Test multiple independent closures."""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "make_multiplier",
                    ("factor",),
                    (
                        (
                            "func_def",
                            "multiply",
                            ("x",),
                            (("return", ("*", ("name", "x"), ("name", "factor"))),),
                        ),
                        ("return", ("name", "multiply")),
                    ),
                ),
                (
                    "assign",
                    "double",
                    ("call", ("name", "make_multiplier"), (("const", 2),), ()),
                    None,
                ),
                (
                    "assign",
                    "triple",
                    ("call", ("name", "make_multiplier"), (("const", 3),), ()),
                    None,
                ),
                (
                    "assign",
                    "result1",
                    ("call", ("name", "double"), (("const", 4),), ()),
                    None,
                ),
                (
                    "assign",
                    "result2",
                    ("call", ("name", "triple"), (("const", 4),), ()),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result1") == 8
        assert self.interpreter._get_variable("result2") == 12

    def test_closure_with_multiple_variables(self):
        """Test closure capturing multiple variables."""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "make_polynomial",
                    ("a", "b", "c"),
                    (
                        (
                            "func_def",
                            "poly",
                            ("x",),
                            (
                                (
                                    "return",
                                    (
                                        "+",
                                        (
                                            "+",
                                            (
                                                "*",
                                                ("name", "a"),
                                                ("**", ("name", "x"), ("const", 2)),
                                            ),
                                            ("*", ("name", "b"), ("name", "x")),
                                        ),
                                        ("name", "c"),
                                    ),
                                ),
                            ),
                        ),
                        ("return", ("name", "poly")),
                    ),
                ),
                (
                    "assign",
                    "f1",
                    (
                        "call",
                        ("name", "make_polynomial"),
                        (("const", 1), ("const", 0), ("const", 0)),
                        (),
                    ),
                    None,
                ),
                (
                    "assign",
                    "f2",
                    (
                        "call",
                        ("name", "make_polynomial"),
                        (("const", 2), ("const", 3), ("const", 1)),
                        (),
                    ),
                    None,
                ),
                (
                    "assign",
                    "result1",
                    ("call", ("name", "f1"), (("const", 5),), ()),
                    None,
                ),
                (
                    "assign",
                    "result2",
                    ("call", ("name", "f2"), (("const", 5),), ()),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result1") == 25  # 1*5^2 + 0*5 + 0
        assert self.interpreter._get_variable("result2") == 66  # 2*5^2 + 3*5 + 1

    def test_nested_closure(self):
        """Test nested closures."""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "make_outer",
                    ("x",),
                    (
                        (
                            "func_def",
                            "make_inner",
                            ("y",),
                            (
                                (
                                    "func_def",
                                    "innermost",
                                    ("z",),
                                    (
                                        (
                                            "return",
                                            (
                                                "+",
                                                ("+", ("name", "x"), ("name", "y")),
                                                ("name", "z"),
                                            ),
                                        ),
                                    ),
                                ),
                                ("return", ("name", "innermost")),
                            ),
                        ),
                        ("return", ("name", "make_inner")),
                    ),
                ),
                (
                    "assign",
                    "outer_func",
                    ("call", ("name", "make_outer"), (("const", 10),), ()),
                    None,
                ),
                (
                    "assign",
                    "inner_func",
                    ("call", ("name", "outer_func"), (("const", 20),), ()),
                    None,
                ),
                (
                    "assign",
                    "result",
                    ("call", ("name", "inner_func"), (("const", 30),), ()),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") == 60  # 10 + 20 + 30

    def test_pure_closure_behavior(self):
        """Test that closures are pure (don't modify captured variables)."""
        # This is a regression test to ensure we maintain pure closure behavior
        # and don't accidentally implement non-pure closures
        ir = (
            "module",
            (
                (
                    "func_def",
                    "make_counter",
                    (),
                    (
                        ("assign", "count", ("const", 0), None),
                        (
                            "func_def",
                            "increment",
                            (),
                            (
                                (
                                    "assign",
                                    "count",
                                    ("+", ("name", "count"), ("const", 1)),
                                    None,
                                ),
                                ("return", ("name", "count")),
                            ),
                        ),
                        ("return", ("name", "increment")),
                    ),
                ),
                ("assign", "counter", ("call", ("name", "make_counter"), (), ()), None),
                ("assign", "result1", ("call", ("name", "counter"), (), ()), None),
                ("assign", "result2", ("call", ("name", "counter"), (), ()), None),
                ("assign", "result3", ("call", ("name", "counter"), (), ()), None),
            ),
        )
        self.interpreter.execute_program(ir)

        # In pure closures, each call should return 1 (count starts at 0 each time)
        # In non-pure closures, it would return 1, 2, 3
        assert self.interpreter._get_variable("result1") == 1
        assert self.interpreter._get_variable("result2") == 1
        assert self.interpreter._get_variable("result3") == 1

    def test_closure_variable_isolation(self):
        """Test that closure variables are isolated (copied, not referenced)."""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "make_accumulator",
                    ("initial",),
                    (
                        ("assign", "total", ("name", "initial"), None),
                        (
                            "func_def",
                            "add",
                            ("value",),
                            (
                                (
                                    "assign",
                                    "total",
                                    ("+", ("name", "total"), ("name", "value")),
                                    None,
                                ),
                                ("return", ("name", "total")),
                            ),
                        ),
                        ("return", ("name", "add")),
                    ),
                ),
                (
                    "assign",
                    "acc1",
                    ("call", ("name", "make_accumulator"), (("const", 10),), ()),
                    None,
                ),
                (
                    "assign",
                    "acc2",
                    ("call", ("name", "make_accumulator"), (("const", 20),), ()),
                    None,
                ),
                (
                    "assign",
                    "result1a",
                    ("call", ("name", "acc1"), (("const", 5),), ()),
                    None,
                ),
                (
                    "assign",
                    "result1b",
                    ("call", ("name", "acc1"), (("const", 3),), ()),
                    None,
                ),
                (
                    "assign",
                    "result2a",
                    ("call", ("name", "acc2"), (("const", 7),), ()),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)

        # In pure closures, each accumulator starts fresh each time
        # acc1 with initial=10: add(5) = 15, add(3) = 13 (not 18!)
        # acc2 with initial=20: add(7) = 27
        assert self.interpreter._get_variable("result1a") == 15  # 10 + 5
        assert self.interpreter._get_variable("result1b") == 13  # 10 + 3 (not 18!)
        assert self.interpreter._get_variable("result2a") == 27  # 20 + 7


class TestTupleUnpackingIR:
    """Tests for tuple unpacking assignment in IR interpreter."""

    def setup_method(self):
        """Setup for each test method."""
        self.interpreter = IRInterpreter()

    def test_basic_tuple_unpacking(self):
        """Test basic tuple unpacking assignment."""
        ir = (
            "module",
            (("tuple_assign", ("a", "b"), ("tuple", (("const", 1), ("const", 2)))),),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("a") == 1
        assert self.interpreter._get_variable("b") == 2

    def test_variable_swap(self):
        """Test variable swapping with tuple unpacking."""
        ir = (
            "module",
            (
                ("assign", "x", ("const", 10), None),
                ("assign", "y", ("const", 20), None),
                ("tuple_assign", ("x", "y"), ("tuple", (("name", "y"), ("name", "x")))),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == 20
        assert self.interpreter._get_variable("y") == 10

    def test_list_unpacking(self):
        """Test unpacking from a list."""
        ir = (
            "module",
            (
                (
                    "assign",
                    "nums",
                    ("list", (("const", 100), ("const", 200), ("const", 300))),
                    None,
                ),
                ("tuple_assign", ("a", "b", "c"), ("name", "nums")),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("a") == 100
        assert self.interpreter._get_variable("b") == 200
        assert self.interpreter._get_variable("c") == 300

    def test_string_unpacking(self):
        """Test unpacking from a string."""
        ir = (
            "module",
            (
                ("assign", "s", ("const", "hi"), None),
                ("tuple_assign", ("c1", "c2"), ("name", "s")),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("c1") == "h"
        assert self.interpreter._get_variable("c2") == "i"

    def test_tuple_unpacking_too_many_values(self):
        """Test error when too many values to unpack."""
        ir = (
            "module",
            (
                (
                    "tuple_assign",
                    ("a", "b"),
                    ("tuple", (("const", 1), ("const", 2), ("const", 3))),
                ),
            ),
        )
        with pytest.raises(
            ValueError, match="too many values to unpack \\(expected 2\\)"
        ):
            self.interpreter.execute_program(ir)

    def test_tuple_unpacking_not_enough_values(self):
        """Test error when not enough values to unpack."""
        ir = (
            "module",
            (
                (
                    "tuple_assign",
                    ("a", "b", "c"),
                    ("tuple", (("const", 1), ("const", 2))),
                ),
            ),
        )
        with pytest.raises(
            ValueError, match="not enough values to unpack \\(expected 3, got 2\\)"
        ):
            self.interpreter.execute_program(ir)

    def test_tuple_unpacking_non_sequence(self):
        """Test error when trying to unpack a non-sequence."""
        ir = ("module", (("tuple_assign", ("a", "b"), ("const", 42)),))
        with pytest.raises(TypeError, match="cannot unpack non-sequence int"):
            self.interpreter.execute_program(ir)

    def test_fibonacci_with_tuple_unpacking(self):
        """Test Fibonacci function using tuple unpacking."""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "fibonacci",
                    ("n",),
                    (
                        (
                            "if",
                            ("<=", ("name", "n"), ("const", 1)),
                            (("return", ("name", "n")),),
                            (
                                (
                                    "tuple_assign",
                                    ("a", "b"),
                                    ("tuple", (("const", 0), ("const", 1))),
                                ),
                                (
                                    "for",
                                    ("name", "i"),
                                    (
                                        "call",
                                        ("name", "range"),
                                        (
                                            ("const", 2),
                                            ("+", ("name", "n"), ("const", 1)),
                                        ),
                                        (),
                                    ),
                                    (
                                        (
                                            "tuple_assign",
                                            ("a", "b"),
                                            (
                                                "tuple",
                                                (
                                                    ("name", "b"),
                                                    ("+", ("name", "a"), ("name", "b")),
                                                ),
                                            ),
                                        ),
                                    ),
                                    (),
                                ),
                                ("return", ("name", "b")),
                            ),
                        ),
                    ),
                ),
                (
                    "assign",
                    "result",
                    ("call", ("name", "fibonacci"), (("const", 5),), ()),
                    None,
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") == 5


class TestMultipleTargetAssignmentIRInterpreter:
    """Tests for multiple target assignment IR execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interpreter = IRInterpreter()

    def test_simple_multiple_assignment(self):
        """Test execution of simple multiple assignment: a = b = 1"""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        ("assign", "a", ("const", 1), None),
                        ("assign", "b", ("const", 1), None),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("a") == 1
        assert self.interpreter._get_variable("b") == 1

    def test_three_target_assignment(self):
        """Test execution of three target assignment: x = y = z = 'hello'"""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        ("assign", "x", ("const", "hello"), None),
                        ("assign", "y", ("const", "hello"), None),
                        ("assign", "z", ("const", "hello"), None),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == "hello"
        assert self.interpreter._get_variable("y") == "hello"
        assert self.interpreter._get_variable("z") == "hello"

    def test_multiple_assignment_with_expression(self):
        """Test execution of multiple assignment with expression: a = b = 2 + 3"""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        ("assign", "a", ("+", ("const", 2), ("const", 3)), None),
                        ("assign", "b", ("+", ("const", 2), ("const", 3)), None),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("a") == 5
        assert self.interpreter._get_variable("b") == 5

    def test_multiple_assignment_independence(self):
        """Test that variables assigned together are independent for immutable types."""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        ("assign", "a", ("const", 100), None),
                        ("assign", "b", ("const", 100), None),
                        ("assign", "c", ("const", 100), None),
                    ),
                ),
                ("assign", "a", ("const", 200), None),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("a") == 200
        assert self.interpreter._get_variable("b") == 100
        assert self.interpreter._get_variable("c") == 100

    def test_multiple_assignment_with_list(self):
        """Test multiple assignment with mutable objects (list)."""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        (
                            "assign",
                            "list1",
                            ("list", (("const", 1), ("const", 2), ("const", 3))),
                            None,
                        ),
                        (
                            "assign",
                            "list2",
                            ("list", (("const", 1), ("const", 2), ("const", 3))),
                            None,
                        ),
                    ),
                ),
                ("subscript_assign", ("name", "list1"), ("const", 0), ("const", 999)),
            ),
        )
        self.interpreter.execute_program(ir)
        list1 = self.interpreter._get_variable("list1")
        list2 = self.interpreter._get_variable("list2")
        # Lists are separate objects, so modifying one doesn't affect the other
        assert list1 == [999, 2, 3]
        assert list2 == [1, 2, 3]

    def test_multiple_assignment_with_subscript(self):
        """Test multiple assignment combined with subscript assignment."""
        ir = (
            "module",
            (
                (
                    "assign",
                    "arr1",
                    ("list", (("const", 0), ("const", 0), ("const", 0))),
                    None,
                ),
                (
                    "assign",
                    "arr2",
                    ("list", (("const", 0), ("const", 0), ("const", 0))),
                    None,
                ),
                (
                    "multi_assign",
                    (
                        (
                            "subscript_assign",
                            ("name", "arr1"),
                            ("const", 0),
                            ("const", 99),
                        ),
                        (
                            "subscript_assign",
                            ("name", "arr2"),
                            ("const", 1),
                            ("const", 99),
                        ),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        arr1 = self.interpreter._get_variable("arr1")
        arr2 = self.interpreter._get_variable("arr2")
        assert arr1 == [99, 0, 0]
        assert arr2 == [0, 99, 0]

    def test_multiple_assignment_with_tuple_unpacking(self):
        """Test multiple assignment combined with tuple unpacking."""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        (
                            "tuple_assign",
                            ("a", "b"),
                            ("list", (("const", 10), ("const", 20))),
                        ),
                        (
                            "tuple_assign",
                            ("c", "d"),
                            ("list", (("const", 10), ("const", 20))),
                        ),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("a") == 10
        assert self.interpreter._get_variable("b") == 20
        assert self.interpreter._get_variable("c") == 10
        assert self.interpreter._get_variable("d") == 20

    def test_mixed_simple_and_tuple_assignment(self):
        """Test mixing simple and tuple assignment targets."""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        (
                            "assign",
                            "x",
                            ("list", (("const", 100), ("const", 200))),
                            None,
                        ),
                        (
                            "tuple_assign",
                            ("y", "z"),
                            ("list", (("const", 100), ("const", 200))),
                        ),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("x") == [100, 200]
        assert self.interpreter._get_variable("y") == 100
        assert self.interpreter._get_variable("z") == 200

    def test_many_target_assignment(self):
        """Test assignment with many targets."""
        ir = (
            "module",
            (
                (
                    "multi_assign",
                    (
                        ("assign", "a", ("const", 123), None),
                        ("assign", "b", ("const", 123), None),
                        ("assign", "c", ("const", 123), None),
                        ("assign", "d", ("const", 123), None),
                        ("assign", "e", ("const", 123), None),
                        ("assign", "f", ("const", 123), None),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("a") == 123
        assert self.interpreter._get_variable("b") == 123
        assert self.interpreter._get_variable("c") == 123
        assert self.interpreter._get_variable("d") == 123
        assert self.interpreter._get_variable("e") == 123
        assert self.interpreter._get_variable("f") == 123

    def test_multiple_assignment_in_function(self):
        """Test multiple assignment inside a function."""
        ir = (
            "module",
            (
                (
                    "func_def",
                    "test_func",
                    (),
                    (
                        (
                            "multi_assign",
                            (
                                ("assign", "a", ("const", 42), None),
                                ("assign", "b", ("const", 42), None),
                                ("assign", "c", ("const", 42), None),
                            ),
                        ),
                        (
                            "return",
                            ("+", ("+", ("name", "a"), ("name", "b")), ("name", "c")),
                        ),
                    ),
                ),
                ("assign", "result", ("call", ("name", "test_func"), (), ()), None),
            ),
        )
        self.interpreter.execute_program(ir)
        assert self.interpreter._get_variable("result") == 126

    def test_multiple_assignment_different_types(self):
        """Test multiple assignment with different data types."""
        ir = (
            "module",
            (
                # Numbers
                (
                    "multi_assign",
                    (
                        ("assign", "num1", ("const", 42), None),
                        ("assign", "num2", ("const", 42), None),
                    ),
                ),
                # Strings
                (
                    "multi_assign",
                    (
                        ("assign", "str1", ("const", "test"), None),
                        ("assign", "str2", ("const", "test"), None),
                    ),
                ),
                # Lists
                (
                    "multi_assign",
                    (
                        (
                            "assign",
                            "list1",
                            ("list", (("const", 1), ("const", 2), ("const", 3))),
                            None,
                        ),
                        (
                            "assign",
                            "list2",
                            ("list", (("const", 1), ("const", 2), ("const", 3))),
                            None,
                        ),
                    ),
                ),
                # Booleans
                (
                    "multi_assign",
                    (
                        ("assign", "bool1", ("const", True), None),
                        ("assign", "bool2", ("const", True), None),
                    ),
                ),
            ),
        )
        self.interpreter.execute_program(ir)

        assert self.interpreter._get_variable("num1") == 42
        assert self.interpreter._get_variable("num2") == 42
        assert self.interpreter._get_variable("str1") == "test"
        assert self.interpreter._get_variable("str2") == "test"
        assert self.interpreter._get_variable("list1") == [1, 2, 3]
        assert self.interpreter._get_variable("list2") == [1, 2, 3]
        assert self.interpreter._get_variable("bool1") is True
        assert self.interpreter._get_variable("bool2") is True


class TestGenericEnumTypedef:
    """Tests for generic enum typedef handling in IR interpreter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interpreter = IRInterpreter()

    def test_enum_type_storage(self):
        """Test that enum types are properly stored without hardcoded constants."""
        ir = ("module", (("typedef", "MyEnum", "Enum"),))
        self.interpreter.execute_program(ir)

        # Check that the enum type is stored
        assert "MyEnum" in self.interpreter.enum_types
        assert self.interpreter.enum_types["MyEnum"] == "Enum"

    def test_multiple_enum_types(self):
        """Test storing multiple different enum types."""
        ir = (
            "module",
            (
                ("typedef", "Color", "Enum"),
                ("typedef", "Direction", "Enum"),
            ),
        )
        self.interpreter.execute_program(ir)

        assert "Color" in self.interpreter.enum_types
        assert "Direction" in self.interpreter.enum_types
        assert self.interpreter.enum_types["Color"] == "Enum"
        assert self.interpreter.enum_types["Direction"] == "Enum"

    def test_enum_with_constants_list_extensibility(self):
        """Test future extensibility for enum with constants list."""
        # This test demonstrates potential future support for enum constants
        # Current implementation only stores the type, but could be extended
        # to handle: ("typedef", "Status", ("Enum", ["PENDING", "RUNNING", "COMPLETED"]))

        # For now, test basic enum type registration
        ir = ("module", (("typedef", "Status", "Enum"),))
        self.interpreter.execute_program(ir)

        assert "Status" in self.interpreter.enum_types
        assert self.interpreter.enum_types["Status"] == "Enum"

        # Future enhancement could automatically define:
        # Status_PENDING = 0, Status_RUNNING = 1, Status_COMPLETED = 2
        # when constants list is provided in the IR format
