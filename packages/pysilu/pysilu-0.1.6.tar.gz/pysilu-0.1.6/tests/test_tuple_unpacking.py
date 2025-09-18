"""Test tuple unpacking in for loops."""

import ast
import pytest
from silu.interpreter import SiluInterpreter
from silu.ir_interpreter import IRInterpreter
from silu.ir_generator import SiluIRGenerator


class TestTupleUnpacking:
    """Test tuple unpacking functionality in for loops."""

    def test_basic_tuple_unpacking(self):
        """Test basic tuple unpacking with list of tuples."""
        code = """
result = []
for x, y in [(1, 2), (3, 4), (5, 6)]:
    result.append(x + y)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        result = interpreter.env.get("result")
        assert result == [3, 7, 11]

    def test_dict_items_unpacking(self):
        """Test tuple unpacking with dict.items()."""
        code = """
d = {'a': 1, 'b': 2, 'c': 3}
keys = []
values = []
for key, value in d.items():
    keys.append(key)
    values.append(value)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        keys = interpreter.env.get("keys")
        values = interpreter.env.get("values")

        # Sort both lists since dict order is not guaranteed
        keys.sort()
        values.sort()
        assert keys == ["a", "b", "c"]
        assert values == [1, 2, 3]

    def test_three_element_unpacking(self):
        """Test unpacking with three elements."""
        code = """
data = [('Alice', 25, 'Engineer'), ('Bob', 30, 'Designer')]
names = []
ages = []
jobs = []
for name, age, job in data:
    names.append(name)
    ages.append(age)
    jobs.append(job)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("names") == ["Alice", "Bob"]
        assert interpreter.env.get("ages") == [25, 30]
        assert interpreter.env.get("jobs") == ["Engineer", "Designer"]

    def test_unpacking_with_calculation(self):
        """Test using unpacked values in calculations."""
        code = """
prices = {'apple': 1.5, 'banana': 0.8, 'orange': 2.0}
total = 0
for item, price in prices.items():
    total = total + price
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        total = interpreter.env.get("total")
        assert total == 4.3

    def test_empty_sequence_unpacking(self):
        """Test unpacking with empty sequence."""
        code = """
result = 0
for x, y in []:
    result = result + 1
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == 0

    def test_unpacking_error_non_sequence(self):
        """Test error when trying to unpack non-sequence."""
        code = """
for x, y in [1, 2, 3]:
    pass
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(ValueError, match="Cannot unpack non-sequence"):
            interpreter.visit(tree)

    def test_unpacking_error_wrong_size_too_many(self):
        """Test error when tuple has too many values."""
        code = """
for x, y in [(1, 2, 3)]:
    pass
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(ValueError, match="Too many values to unpack"):
            interpreter.visit(tree)

    def test_unpacking_error_wrong_size_too_few(self):
        """Test error when tuple has too few values."""
        code = """
for x, y, z in [(1, 2)]:
    pass
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        with pytest.raises(ValueError, match="Too many values to unpack"):
            interpreter.visit(tree)

    def test_unpacking_with_nested_data(self):
        """Test unpacking with nested data structures."""
        code = """
data = [('group1', [1, 2]), ('group2', [3, 4])]
result = {}
for name, values in data:
    total = 0
    for val in values:
        total = total + val
    result[name] = total
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        result = interpreter.env.get("result")
        assert result == {"group1": 3, "group2": 7}

    def test_unpacking_with_break_continue(self):
        """Test unpacking with break and continue statements."""
        code = """
data = [('a', 1), ('b', 2), ('c', 3), ('d', 4)]
result = []
for key, value in data:
    if key == 'b':
        continue
    if key == 'd':
        break
    result.append(value)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == [1, 3]


class TestTupleUnpackingIR:
    """Test tuple unpacking in IR execution."""

    def test_ir_basic_tuple_unpacking(self):
        """Test basic tuple unpacking in IR execution."""
        code = """
result = []
for x, y in [(1, 2), (3, 4)]:
    result.append(x + y)
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        result = ir_interpreter._get_variable("result")
        assert result == [3, 7]

    def test_ir_dict_items_unpacking(self):
        """Test dict.items() unpacking in IR execution."""
        code = """
d = {'x': 10, 'y': 20}
total = 0
for key, value in d.items():
    total = total + value
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        total = ir_interpreter._get_variable("total")
        assert total == 30

    def test_ir_unpacking_error_handling(self):
        """Test error handling in IR execution."""
        code = """
for x, y in [1, 2]:
    pass
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        with pytest.raises(ValueError, match="Cannot unpack non-sequence"):
            ir_interpreter.execute(ir)


class TestTupleUnpackingEdgeCases:
    """Test edge cases for tuple unpacking."""

    def test_unpacking_with_single_variable(self):
        """Test that single variable assignment still works."""
        code = """
result = []
for item in [(1, 2), (3, 4)]:
    result.append(item)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        result = interpreter.env.get("result")
        assert result == [(1, 2), (3, 4)]

    def test_unpacking_mixed_sequences(self):
        """Test unpacking with both tuples and lists."""
        code = """
data = [(1, 2), [3, 4]]
result = []
for x, y in data:
    result.append(x + y)
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        result = interpreter.env.get("result")
        assert result == [3, 7]

    def test_unpacking_variable_shadowing(self):
        """Test that unpacking variables properly shadow outer scope."""
        code = """
x = 100
y = 200
result = []
for x, y in [(1, 2), (3, 4)]:
    result.append(x + y)
# x and y should be the last values from the loop
final_x = x
final_y = y
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        assert interpreter.env.get("result") == [3, 7]
        assert interpreter.env.get("final_x") == 3
        assert interpreter.env.get("final_y") == 4

    def test_unsupported_complex_unpacking(self):
        """Test that complex unpacking patterns are not supported."""
        import ast

        # Try to parse complex unpacking (nested)
        code_with_nested = "for (a, b), c in [((1, 2), 3)]: pass"
        tree = ast.parse(code_with_nested)
        interpreter = SiluInterpreter()

        # This should raise NotImplementedError for complex patterns
        with pytest.raises(
            NotImplementedError, match="Only simple names are supported"
        ):
            interpreter.visit(tree)
