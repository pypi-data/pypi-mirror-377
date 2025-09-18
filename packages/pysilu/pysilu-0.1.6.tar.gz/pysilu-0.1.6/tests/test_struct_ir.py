#!/usr/bin/env python3
"""
Tests for struct functionality in the IR interpreter.
"""

import pytest
from silu.ir_interpreter import IRInterpreter


class TestStructIR:
    """Test struct type definitions and operations in IR interpreter."""

    def test_typedef_struct_definition(self):
        """Test basic struct type definition."""
        interpreter = IRInterpreter()

        # Define a struct type
        interpreter.execute(("typedef_struct", "Point", (("x", "int"), ("y", "int"))))

        # Check that the struct type is registered
        assert "Point" in interpreter.struct_types
        assert interpreter.struct_types["Point"] == (("x", "int"), ("y", "int"))

    def test_struct_instance_creation(self):
        """Test creating struct instances."""
        interpreter = IRInterpreter()

        # Define struct type and create instance
        ir = (
            "module",
            (
                ("typedef_struct", "Point", (("x", "int"), ("y", "int"))),
                ("assign", "p", None, "struct_Point"),
            ),
        )

        # result =
        interpreter.execute(ir)

        # Check that the instance is created with default values
        p = interpreter._get_variable("p")
        assert isinstance(p, dict)
        assert p == {"x": 0, "y": 0}
        assert id(p) in interpreter.struct_instances

    def test_struct_attribute_access(self):
        """Test accessing struct attributes."""
        ir_data = (
            "module",
            (
                ("typedef_struct", "Point", (("x", "int"), ("y", "int"))),
                ("assign", "p", None, "struct_Point"),
                ("assign", ("attribute", ("name", "p"), "x"), ("const", 5), None),
                ("assign", ("attribute", ("name", "p"), "y"), ("const", 10), None),
            ),
        )

        interpreter = IRInterpreter()
        interpreter.execute(ir_data)

        p = interpreter._get_variable("p")
        assert p["x"] == 5
        assert p["y"] == 10

    def test_struct_attribute_in_expressions(self):
        """Test using struct attributes in expressions."""
        ir_data = (
            "module",
            (
                ("typedef_struct", "Point", (("x", "int"), ("y", "int"))),
                ("assign", "p", None, "struct_Point"),
                ("assign", ("attribute", ("name", "p"), "x"), ("const", 3), None),
                ("assign", ("attribute", ("name", "p"), "y"), ("const", 4), None),
                (
                    "assign",
                    "distance_squared",
                    (
                        "+",
                        (
                            "*",
                            ("attribute", ("name", "p"), "x"),
                            ("attribute", ("name", "p"), "x"),
                        ),
                        (
                            "*",
                            ("attribute", ("name", "p"), "y"),
                            ("attribute", ("name", "p"), "y"),
                        ),
                    ),
                    None,
                ),
            ),
        )

        interpreter = IRInterpreter()
        interpreter.execute(ir_data)

        # 3^2 + 4^2 = 9 + 16 = 25
        assert interpreter._get_variable("distance_squared") == 25

    def test_struct_with_different_field_types(self):
        """Test struct with different field types."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                (
                    "typedef_struct",
                    "Person",
                    (
                        ("name", "str"),
                        ("age", "int"),
                        ("height", "float"),
                        ("active", "bool"),
                    ),
                ),
                ("assign", "person", None, "struct_Person"),
            ),
        )

        interpreter.execute(ir)
        person = interpreter._get_variable("person")

        assert person == {"name": "", "age": 0, "height": 0.0, "active": False}

    def test_struct_undefined_type_auto_creation(self):
        """Test auto-creation of undefined struct types."""
        interpreter = IRInterpreter()

        # Execute assignment with undefined struct type
        interpreter.execute(("assign", "x", None, "struct_UndefinedStruct"))

        # Verify the struct type was auto-created
        assert "UndefinedStruct" in interpreter.struct_types
        assert interpreter.struct_types["UndefinedStruct"] == []  # Empty field list

        # Verify the variable was created as an empty struct
        x = interpreter.global_env["x"]
        assert isinstance(x, dict)
        assert x == {}  # Empty struct instance
        assert id(x) in interpreter.struct_instances  # Tracked as struct instance

    def test_struct_attribute_error(self):
        """Test error when accessing non-existent struct attribute."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("typedef_struct", "Point", (("x", "int"), ("y", "int"))),
                ("assign", "p", None, "struct_Point"),
            ),
        )

        interpreter.execute(ir)

        with pytest.raises(AttributeError, match="struct object has no attribute 'z'"):
            interpreter.execute(("attribute", ("name", "p"), "z"))

    def test_regular_dict_still_works(self):
        """Test that regular dictionaries still work with getattr."""
        interpreter = IRInterpreter()

        # Create a regular dictionary (not a struct)
        test_dict = {"a": 1, "b": 2}
        interpreter.execute(("assign", "d", test_dict, None))

        # This should use getattr, not struct attribute access, which should work
        # because regular dicts have methods like 'items'
        try:
            result = interpreter.execute(
                ("call", ("attribute", ("name", "d"), "items"), (), ())
            )
            # If this works, the dict is being treated as a regular dict, not a struct
            assert callable(result) or hasattr(result, "__iter__")
        except AttributeError:
            # This would indicate the dict is being treated as a struct, which is wrong
            pytest.fail("Regular dictionary was treated as struct")

    def test_struct_in_function_main(self):
        """Test the exact IR structure from 00024.ir.json."""
        ir_data = (
            "module",
            (
                ("typedef_struct", "s", (("x", "int"), ("y", "int"))),
                ("assign", "v", None, "struct_s"),
                (
                    "func_def",
                    "main",
                    (),
                    (
                        (
                            "assign",
                            ("attribute", ("name", "v"), "x"),
                            ("const", 1),
                            None,
                        ),
                        (
                            "assign",
                            ("attribute", ("name", "v"), "y"),
                            ("const", 2),
                            None,
                        ),
                        (
                            "return",
                            (
                                "-",
                                ("-", ("const", 3), ("attribute", ("name", "v"), "x")),
                                ("attribute", ("name", "v"), "y"),
                            ),
                        ),
                    ),
                    (),
                    "int",
                ),
            ),
        )

        interpreter = IRInterpreter()
        result = interpreter.execute_program(ir_data)

        # Should return 3 - 1 - 2 = 0
        assert result == 0

    def test_multiple_struct_types(self):
        """Test defining and using multiple struct types."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("typedef_struct", "Point", (("x", "int"), ("y", "int"))),
                ("typedef_struct", "Color", (("r", "int"), ("g", "int"), ("b", "int"))),
                ("assign", "p", None, "struct_Point"),
                ("assign", "c", None, "struct_Color"),
            ),
        )

        interpreter.execute(ir)

        p = interpreter._get_variable("p")
        c = interpreter._get_variable("c")

        assert p == {"x": 0, "y": 0}
        assert c == {"r": 0, "g": 0, "b": 0}
        assert id(p) in interpreter.struct_instances
        assert id(c) in interpreter.struct_instances

    def test_struct_instance_independence(self):
        """Test that different struct instances are independent."""
        interpreter = IRInterpreter()

        ir = (
            "module",
            (
                ("typedef_struct", "Point", (("x", "int"), ("y", "int"))),
                ("assign", "p1", None, "struct_Point"),
                ("assign", "p2", None, "struct_Point"),
                ("assign", ("attribute", ("name", "p1"), "x"), ("const", 10), None),
                ("assign", ("attribute", ("name", "p2"), "x"), ("const", 20), None),
            ),
        )

        interpreter.execute(ir)

        p1 = interpreter._get_variable("p1")
        p2 = interpreter._get_variable("p2")

        assert p1["x"] == 10
        assert p2["x"] == 20
        assert p1["y"] == 0  # unchanged
        assert p2["y"] == 0  # unchanged
