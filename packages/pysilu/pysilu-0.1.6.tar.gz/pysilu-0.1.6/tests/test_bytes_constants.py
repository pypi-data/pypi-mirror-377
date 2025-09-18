"""Test bytes constants in IR execution."""

import ast
from silu.interpreter import SiluInterpreter
from silu.ir_interpreter import IRInterpreter
from silu.ir_generator import SiluIRGenerator


class TestBytesConstants:
    """Test bytes constants functionality in interpreter and IR execution."""

    def test_basic_bytes_interpreter(self):
        """Test basic bytes constants in direct interpreter."""
        code = """
result = b"hello"
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        result = interpreter.env.get("result")
        assert result == b"hello"
        assert isinstance(result, bytes)

    def test_empty_bytes_interpreter(self):
        """Test empty bytes constant."""
        code = """
result = b""
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)
        result = interpreter.env.get("result")
        assert result == b""
        assert isinstance(result, bytes)

    def test_bytes_with_escapes_interpreter(self):
        """Test bytes with escape sequences."""
        code = """
newline = b"line1\\nline2"
tab = b"col1\\tcol2"
null = b"\\x00"
high = b"\\xff"
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)

        assert interpreter.env.get("newline") == b"line1\nline2"
        assert interpreter.env.get("tab") == b"col1\tcol2"
        assert interpreter.env.get("null") == b"\x00"
        assert interpreter.env.get("high") == b"\xff"

    def test_bytes_comparison_interpreter(self):
        """Test bytes comparison operations."""
        code = """
equal = b"test" == b"test"
not_equal = b"test" != b"other"
mixed_equal = b"1" == 1
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)

        assert interpreter.env.get("equal") is True
        assert interpreter.env.get("not_equal") is True
        assert interpreter.env.get("mixed_equal") is False

    def test_bytes_operations_interpreter(self):
        """Test bytes arithmetic operations."""
        code = """
concat = b"hello" + b"world"
repeat = b"abc" * 3
"""
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)

        assert interpreter.env.get("concat") == b"helloworld"
        assert interpreter.env.get("repeat") == b"abcabcabc"

    def test_ir_basic_bytes_constant(self):
        """Test basic bytes constant in IR execution."""
        code = """
result = b"hello"
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Check that const_b is generated
        ir_str = str(ir)
        assert "const_b" in ir_str

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        result = ir_interpreter._get_variable("result")
        assert result == b"hello"
        assert isinstance(result, bytes)

    def test_ir_empty_bytes_constant(self):
        """Test empty bytes constant in IR execution."""
        code = """
result = b""
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        result = ir_interpreter._get_variable("result")
        assert result == b""
        assert isinstance(result, bytes)

    def test_ir_bytes_with_escapes(self):
        """Test bytes with escape sequences in IR execution."""
        code = """
newline = b"line1\\nline2"
null = b"\\x00"
high = b"\\xff"
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        assert ir_interpreter._get_variable("newline") == b"line1\nline2"
        assert ir_interpreter._get_variable("null") == b"\x00"
        assert ir_interpreter._get_variable("high") == b"\xff"

    def test_ir_bytes_comparison(self):
        """Test bytes comparison in IR execution."""
        code = """
equal = b"test" == b"test"
not_equal = b"test" != b"other"
mixed = b"1" == 1
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        assert ir_interpreter._get_variable("equal") is True
        assert ir_interpreter._get_variable("not_equal") is True
        assert ir_interpreter._get_variable("mixed") is False

    def test_ir_bytes_operations(self):
        """Test bytes operations in IR execution."""
        code = """
concat = b"hello" + b"world"
repeat = b"abc" * 3
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        assert ir_interpreter._get_variable("concat") == b"helloworld"
        assert ir_interpreter._get_variable("repeat") == b"abcabcabc"

    def test_ir_bytes_in_expressions(self):
        """Test bytes in complex expressions."""
        code = """
result1 = b"pre" + b"fix" + b"suf"
result2 = b"x" * 2 + b"y" * 3
"""
        # Generate IR
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Execute IR
        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        assert ir_interpreter._get_variable("result1") == b"prefixsuf"
        assert ir_interpreter._get_variable("result2") == b"xxyyy"

    def test_bytes_in_data_structures(self):
        """Test bytes constants in data structures."""
        code = """
bytes_list = [b"first", b"second", b"third"]
bytes_tuple = (b"a", b"b", b"c")
"""
        # Test in interpreter
        interpreter = SiluInterpreter()
        tree = ast.parse(code)
        interpreter.visit(tree)

        bytes_list = interpreter.env.get("bytes_list")
        bytes_tuple = interpreter.env.get("bytes_tuple")

        assert bytes_list == [b"first", b"second", b"third"]
        assert bytes_tuple == (b"a", b"b", b"c")

        # Test in IR
        ir_generator = SiluIRGenerator()
        ir = ir_generator.visit(tree)

        ir_interpreter = IRInterpreter()
        ir_interpreter.execute(ir)

        ir_bytes_list = ir_interpreter._get_variable("bytes_list")
        ir_bytes_tuple = ir_interpreter._get_variable("bytes_tuple")

        assert ir_bytes_list == [b"first", b"second", b"third"]
        assert ir_bytes_tuple == (b"a", b"b", b"c")

    def test_bytes_encoding_roundtrip(self):
        """Test that bytes encoding/decoding roundtrip works correctly."""
        # Test various byte values to ensure latin-1 encoding works
        test_bytes = [
            b"",  # Empty
            b"\x00",  # Null byte
            b"\xff",  # Max byte
            b"\x00\x01\x02\x03",  # Low bytes
            b"\xfc\xfd\xfe\xff",  # High bytes
            b"Hello\x00World\xff",  # Mixed content
        ]

        for original_bytes in test_bytes:
            # Simulate the encoding/decoding process used in IR
            encoded = original_bytes.decode("latin-1")  # What IR generator does
            decoded = encoded.encode("latin-1")  # What IR interpreter does

            assert decoded == original_bytes, f"Roundtrip failed for {original_bytes!r}"

    def test_const_b_ir_structure(self):
        """Test that const_b IR nodes are generated correctly."""
        code = """
test = b"hello"
"""
        ir_generator = SiluIRGenerator()
        tree = ast.parse(code)
        ir = ir_generator.visit(tree)

        # Convert to string to inspect structure
        ir_str = str(ir)

        # Should contain const_b with the string representation
        assert "const_b" in ir_str
        assert "hello" in ir_str
