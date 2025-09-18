#!/usr/bin/env python3
"""
Tests for type annotation conversion functionality in the IR interpreter.
"""

from silu.ir_interpreter import IRInterpreter


class TestTypeAnnotationConversionIR:
    """Test type annotation conversion in IR interpreter."""

    def test_string_to_float_conversion(self):
        """Test conversion of string constants to float with double annotation."""
        interpreter = IRInterpreter()

        ir = ("module", (("assign", "x", ("const", "100.0"), "double"),))

        interpreter.execute(ir)
        x = interpreter._get_variable("x")

        assert isinstance(x, float)
        assert x == 100.0

    def test_string_to_int_conversion(self):
        """Test conversion of string constants to int."""
        interpreter = IRInterpreter()

        ir = ("module", (("assign", "x", ("const", "42"), "int"),))

        interpreter.execute(ir)
        x = interpreter._get_variable("x")

        assert isinstance(x, int)
        assert x == 42

    def test_string_float_to_int_conversion(self):
        """Test conversion of float string to int (should truncate)."""
        interpreter = IRInterpreter()

        ir = ("module", (("assign", "x", ("const", "42.7"), "int"),))

        interpreter.execute(ir)
        x = interpreter._get_variable("x")

        assert isinstance(x, int)
        assert x == 42

    def test_string_to_bool_conversion(self):
        """Test conversion of string constants to bool."""
        interpreter = IRInterpreter()

        # Test true values
        for true_val in ["true", "True", "1", "yes"]:
            ir = ("module", (("assign", "x", ("const", true_val), "bool"),))

            interpreter.execute(ir)
            x = interpreter._get_variable("x")
            assert x is True, f"'{true_val}' should convert to True"

        # Test false values
        for false_val in ["false", "False", "0", "no", ""]:
            ir = ("module", (("assign", "x", ("const", false_val), "bool"),))

            interpreter.execute(ir)
            x = interpreter._get_variable("x")
            assert x is False, f"'{false_val}' should convert to False"

    def test_number_to_string_conversion(self):
        """Test conversion of numbers to string."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("assign", "x", ("const", 42), "str"),
                ("assign", "y", ("const", 3.14), "str"),
            ),
        )

        interpreter.execute(ir)
        x = interpreter._get_variable("x")
        y = interpreter._get_variable("y")

        assert isinstance(x, str)
        assert x == "42"
        assert isinstance(y, str)
        assert y == "3.14"

    def test_comparison_after_conversion(self):
        """Test that comparisons work correctly after type conversion."""
        ir = (
            "module",
            (
                ("assign", "x", ("const", "100.0"), "double"),
                ("assign", "result", ("<", ("name", "x"), ("const", 1)), None),
            ),
        )

        interpreter = IRInterpreter()
        interpreter.execute(ir)

        result = interpreter._get_variable("result")
        assert result is False  # 100.0 < 1 should be False

    def test_arithmetic_after_conversion(self):
        """Test arithmetic operations after type conversion."""
        ir = (
            "module",
            (
                ("assign", "x", ("const", "10.5"), "double"),
                ("assign", "y", ("const", "2.5"), "double"),
                ("assign", "result", ("+", ("name", "x"), ("name", "y")), None),
            ),
        )

        interpreter = IRInterpreter()
        interpreter.execute(ir)

        result = interpreter._get_variable("result")
        assert result == 13.0

    def test_null_value_default_initialization(self):
        """Test that null values still get default initialization."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("assign", "a", None, "int"),
                ("assign", "b", None, "double"),
                ("assign", "c", None, "bool"),
                ("assign", "d", None, "str"),
            ),
        )

        interpreter.execute(ir)

        assert interpreter._get_variable("a") == 0
        assert interpreter._get_variable("b") == 0.0
        assert interpreter._get_variable("c") is False
        assert interpreter._get_variable("d") == ""

    def test_invalid_conversion_keeps_original(self):
        """Test that invalid conversions keep the original value."""
        interpreter = IRInterpreter()

        ir = ("module", (("assign", "x", ("const", "not_a_number"), "int"),))

        interpreter.execute(ir)
        x = interpreter._get_variable("x")

        # Should keep original string value since conversion failed
        assert x == "not_a_number"

    def test_float_annotation_variants(self):
        """Test both 'float' and 'double' annotations work."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("assign", "x", ("const", "3.14"), "float"),
                ("assign", "y", ("const", "2.71"), "double"),
            ),
        )

        interpreter.execute(ir)

        x = interpreter._get_variable("x")
        y = interpreter._get_variable("y")

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert x == 3.14
        assert y == 2.71

    def test_str_annotation_variants(self):
        """Test both 'str' and 'char*' annotations work."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("assign", "x", ("const", 42), "str"),
                ("assign", "y", ("const", 3.14), "char*"),
            ),
        )

        interpreter.execute(ir)

        x = interpreter._get_variable("x")
        y = interpreter._get_variable("y")

        assert isinstance(x, str)
        assert isinstance(y, str)
        assert x == "42"
        assert y == "3.14"

    def test_function_with_type_conversion(self):
        """Test the exact IR structure from 00123.ir.json."""
        ir = (
            "module",
            (
                ("assign", "x", ("const", "100.0"), "double"),
                (
                    "func_def",
                    "main",
                    (),
                    (("return", ("<", ("name", "x"), ("const", 1))),),
                    (),
                    "int",
                ),
            ),
        )

        interpreter = IRInterpreter()
        result = interpreter.execute_program(ir)

        # Should return False (100.0 < 1)
        assert result is False

    def test_multiple_conversions_in_expression(self):
        """Test multiple type conversions within a single expression."""
        ir = (
            "module",
            (
                ("assign", "a", ("const", "10"), "int"),
                ("assign", "b", ("const", "3.14"), "float"),
                ("assign", "c", ("const", "true"), "bool"),
                (
                    "assign",
                    "result",
                    ("+", ("+", ("name", "a"), ("name", "b")), ("name", "c")),
                    None,
                ),
            ),
        )

        interpreter = IRInterpreter()
        interpreter.execute(ir)

        result = interpreter._get_variable("result")
        # 10 + 3.14 + 1 (True as int) = 14.14
        assert result == 14.14

    def test_array_type_annotation_still_works(self):
        """Test that array type annotations still work with the new system."""
        interpreter = IRInterpreter()

        ir = ("module", (("assign", "arr", None, "int[3]"),))

        interpreter.execute(ir)
        arr = interpreter._get_variable("arr")

        assert arr == [0, 0, 0]

    def test_struct_type_annotation_still_works(self):
        """Test that struct type annotations still work with the new system."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("typedef_struct", "Point", (("x", "int"), ("y", "int"))),
                ("assign", "p", None, "struct_Point"),
            ),
        )

        interpreter.execute(ir)
        p = interpreter._get_variable("p")

        assert isinstance(p, dict)
        assert p == {"x": 0, "y": 0}
        assert id(p) in interpreter.struct_instances
