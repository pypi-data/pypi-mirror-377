"""Test memory protection mechanisms."""

import pytest

from silu.ast_processor import process_code


def test_list_multiplication_protection():
    """Test protection against large list multiplication operations."""
    # This should fail with memory protection
    code = """
l = [1, 2, 3]
result = l * 1000001
"""
    with pytest.raises(
        MemoryError, match="Memory protection: Cannot multiply sequence by 1000001"
    ):
        process_code(code)


def test_list_multiplication_reverse_protection():
    """Test protection against large list multiplication (reverse order)."""
    # This should fail with memory protection
    code = """
l = [1, 2, 3]
result = 1000001 * l
"""
    with pytest.raises(
        MemoryError, match="Memory protection: Cannot multiply sequence by 1000001"
    ):
        process_code(code)


def test_string_multiplication_protection():
    """Test protection against large string multiplication operations."""
    # This should fail with memory protection
    code = """
s = "hello"
result = s * 2000001
"""
    with pytest.raises(
        MemoryError, match="Memory protection: Cannot multiply sequence by 2000001"
    ):
        process_code(code)


def test_large_total_elements_protection():
    """Test protection based on total result size."""
    # Even with smaller multiplier, if total elements exceed limit, should fail
    code = """
l = list(range(5000))  # 5000 elements
result = l * 2001      # Would result in 10,005,000 elements (over 10M limit)
"""
    with pytest.raises(
        MemoryError, match="Memory protection: Result would have 10005000 elements"
    ):
        process_code(code)


def test_range_protection():
    """Test protection against large range operations."""
    # This should fail with memory protection
    code = """
result = list(range(10000001))
"""
    with pytest.raises(
        MemoryError, match="Memory protection: range\\(10000001\\) exceeds limit"
    ):
        process_code(code)


def test_range_with_stop_protection():
    """Test protection against range with large stop value."""
    # This should fail with memory protection
    code = """
result = list(range(0, 10000001))
"""
    with pytest.raises(
        MemoryError, match="Memory protection: range\\(.*, 10000001\\) exceeds limit"
    ):
        process_code(code)


def test_extend_with_large_range_protection():
    """Test protection against extend with large range."""
    # This should fail with memory protection (caught at range creation)
    code = """
l = []
l.extend(range(10000001))
"""
    with pytest.raises(
        MemoryError, match="Memory protection: range\\(10000001\\) exceeds limit"
    ):
        process_code(code)


def test_normal_operations_still_work():
    """Test that normal operations within limits still work."""
    code = """
# Normal list multiplication
l1 = [1, 2] * 5
print("List multiplication:", len(l1))

# Normal string multiplication
s1 = "x" * 100
print("String multiplication:", len(s1))

# Normal range
r1 = list(range(1000))
print("Range:", len(r1))

# Normal extend
l2 = []
l2.extend(range(100))
print("Extend:", len(l2))
"""
    # This should work without raising exceptions
    # result =
    process_code(code)
    # No assertion needed - if it doesn't raise an exception, the test passes


def test_boundary_values():
    """Test operations at the exact boundary limits."""
    # Test multiplication at limit (should work)
    code1 = """
l = [1, 2, 3]
result = l * 1000000  # Exactly at limit
print("Length:", len(result))
"""
    # This should work
    process_code(code1)

    # Test range at limit (should work)
    code2 = """
result = list(range(10000000))  # Exactly at limit
print("Length:", len(result))
"""
    # This should work
    process_code(code2)


def test_total_elements_calculation():
    """Test that total elements calculation works correctly."""
    # Small list with smaller multiplier that still exceeds total limit
    code = """
l = list(range(5000))  # 5000 elements
result = l * 500000    # Would result in 2,500,000,000 elements (over 10M limit)
"""
    with pytest.raises(
        MemoryError, match="Memory protection: Result would have 2500000000 elements"
    ):
        process_code(code)


def test_tuple_multiplication_protection():
    """Test protection against large tuple multiplication operations."""
    # This should fail with memory protection
    code = """
t = (1, 2, 3)
result = t * 1000001
"""
    with pytest.raises(
        MemoryError, match="Memory protection: Cannot multiply sequence by 1000001"
    ):
        process_code(code)


def test_zero_and_negative_multipliers():
    """Test that zero and negative multipliers don't trigger protection."""
    code = """
l = [1, 2, 3]
result1 = l * 0        # Should work - results in empty list
result2 = l * -1       # Should work - results in empty list
print("Zero multiplication:", len(result1))
print("Negative multiplication:", len(result2))
"""
    # This should work without raising exceptions
    process_code(code)


def test_memory_error_available():
    """Test that MemoryError is available as a built-in."""
    code = """
print("MemoryError type:", type(MemoryError))
"""
    # This should work - MemoryError should be available
    process_code(code)
