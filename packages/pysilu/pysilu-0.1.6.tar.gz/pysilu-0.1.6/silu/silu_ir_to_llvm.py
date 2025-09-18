"""
Silu IR to LLVM IR Converter

This module converts Silu IR (JSON format) to LLVM IR, enabling compilation
of Silu programs to native machine code.

The converter handles the dynamic typing of Silu by creating a runtime system
with tagged unions for Python-like objects.
"""

import sys
from typing import Any, Dict, Optional
from llvmlite import ir
import llvmlite.binding as llvm
from .ir_utils import parse_ir_from_json_string, IRParseError


class PyObject:
    """Runtime representation of Python objects in LLVM IR."""

    def __init__(self, module: ir.Module):
        self.module = module

        # Define PyObject struct: { i32 type_tag, i8* data }
        self.pyobj_type = ir.LiteralStructType(
            [
                ir.IntType(
                    32
                ),  # type tag (0=int, 1=float, 2=str, 3=bool, 4=list, 5=dict, 6=none)
                ir.PointerType(ir.IntType(8)),  # data pointer
            ]
        )

        # Define string struct: { i32 length, i8* chars }
        self.string_type = ir.LiteralStructType(
            [
                ir.IntType(32),  # length
                ir.PointerType(ir.IntType(8)),  # chars
            ]
        )


class SiluToLLVMConverter:
    """Converts Silu IR to LLVM IR."""

    def __init__(self):
        # Initialize LLVM
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # Get target information
        target = llvm.Target.from_default_triple()
        self.target_machine = target.create_target_machine()

        # Create LLVM module
        self.module = ir.Module(name="silu_module")
        self.module.triple = self.target_machine.triple
        self.module.data_layout = str(self.target_machine.target_data)

        # Runtime object system
        self.pyobj = PyObject(self.module)

        # Global context
        self.variables: Dict[
            str, ir.Value
        ] = {}  # Maps variable names to alloca instructions
        self.functions: Dict[str, ir.Function] = {}
        self.current_function: Optional[ir.Function] = None
        self.current_builder: Optional[ir.IRBuilder] = None

        # Function definitions (IR nodes for later processing)
        self.function_defs: Dict[str, Any] = {}

        # Initialize runtime functions
        self._init_runtime_functions()

    def _init_runtime_functions(self):
        """Initialize runtime support functions."""

        # printf declaration
        printf_ty = ir.FunctionType(
            ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True
        )
        self.printf = ir.Function(self.module, printf_ty, name="printf")

        # malloc and free
        malloc_ty = ir.FunctionType(ir.PointerType(ir.IntType(8)), [ir.IntType(64)])
        self.malloc = ir.Function(self.module, malloc_ty, name="malloc")

        free_ty = ir.FunctionType(ir.VoidType(), [ir.PointerType(ir.IntType(8))])
        self.free = ir.Function(self.module, free_ty, name="free")

        # PyObject creation functions
        self._create_overflow_intrinsics()
        self._create_pyobj_constructors()
        self._create_pyobj_operations()
        self._create_comparison_operations()

    def _create_pyobj_constructors(self):
        """Create PyObject constructor functions."""

        # PyObject* create_int(i64 value)
        create_int_ty = ir.FunctionType(
            ir.PointerType(self.pyobj.pyobj_type), [ir.IntType(64)]
        )
        self.create_int = ir.Function(self.module, create_int_ty, name="create_int")

        block = self.create_int.append_basic_block("entry")
        builder = ir.IRBuilder(block)

        # Allocate PyObject
        obj_ptr = builder.call(
            self.malloc, [ir.Constant(ir.IntType(64), 16)]
        )  # sizeof(PyObject)
        obj = builder.bitcast(obj_ptr, ir.PointerType(self.pyobj.pyobj_type))

        # Set type tag to 0 (int)
        tag_ptr = builder.gep(
            obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        builder.store(ir.Constant(ir.IntType(32), 0), tag_ptr)

        # Allocate and store integer value
        data_ptr = builder.call(
            self.malloc, [ir.Constant(ir.IntType(64), 8)]
        )  # sizeof(i64)
        data_i64 = builder.bitcast(data_ptr, ir.PointerType(ir.IntType(64)))
        builder.store(self.create_int.args[0], data_i64)

        # Store data pointer
        data_ptr_field = builder.gep(
            obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        builder.store(data_ptr, data_ptr_field)

        builder.ret(obj)

        # PyObject* create_str(i8* str, i32 len)
        create_str_ty = ir.FunctionType(
            ir.PointerType(self.pyobj.pyobj_type),
            [ir.PointerType(ir.IntType(8)), ir.IntType(32)],
        )
        self.create_str = ir.Function(self.module, create_str_ty, name="create_str")

        block = self.create_str.append_basic_block("entry")
        builder = ir.IRBuilder(block)

        # Allocate PyObject
        obj_ptr = builder.call(self.malloc, [ir.Constant(ir.IntType(64), 16)])
        obj = builder.bitcast(obj_ptr, ir.PointerType(self.pyobj.pyobj_type))

        # Set type tag to 2 (string)
        tag_ptr = builder.gep(
            obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        builder.store(ir.Constant(ir.IntType(32), 2), tag_ptr)

        # Allocate string struct
        str_ptr = builder.call(
            self.malloc, [ir.Constant(ir.IntType(64), 16)]
        )  # sizeof(string_type)
        str_struct = builder.bitcast(str_ptr, ir.PointerType(self.pyobj.string_type))

        # Store length
        len_ptr = builder.gep(
            str_struct, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        builder.store(self.create_str.args[1], len_ptr)

        # Store chars pointer
        chars_ptr = builder.gep(
            str_struct, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        builder.store(self.create_str.args[0], chars_ptr)

        # Store data pointer
        data_ptr_field = builder.gep(
            obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        builder.store(str_ptr, data_ptr_field)

        builder.ret(obj)

    def _create_pyobj_operations(self):
        """Create PyObject operation functions."""

        # PyObject* pyobj_add(PyObject* left, PyObject* right)
        add_ty = ir.FunctionType(
            ir.PointerType(self.pyobj.pyobj_type),
            [
                ir.PointerType(self.pyobj.pyobj_type),
                ir.PointerType(self.pyobj.pyobj_type),
            ],
        )
        self.pyobj_add = ir.Function(self.module, add_ty, name="pyobj_add")

        block = self.pyobj_add.append_basic_block("entry")
        builder = ir.IRBuilder(block)

        left, right = self.pyobj_add.args

        # Get type tags
        left_tag_ptr = builder.gep(
            left, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        right_tag_ptr = builder.gep(
            right, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        left_tag = builder.load(left_tag_ptr)
        right_tag = builder.load(right_tag_ptr)

        # Check if both are integers (tag == 0)
        both_int_cond = builder.and_(
            builder.icmp_signed("==", left_tag, ir.Constant(ir.IntType(32), 0)),
            builder.icmp_signed("==", right_tag, ir.Constant(ir.IntType(32), 0)),
        )

        int_block = self.pyobj_add.append_basic_block("int_add")
        error_block = self.pyobj_add.append_basic_block("error")
        builder.cbranch(both_int_cond, int_block, error_block)

        # Integer addition
        builder.position_at_end(int_block)

        # Get integer values
        left_data_ptr = builder.gep(
            left, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        right_data_ptr = builder.gep(
            right, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        left_data = builder.load(left_data_ptr)
        right_data = builder.load(right_data_ptr)
        left_i64_ptr = builder.bitcast(left_data, ir.PointerType(ir.IntType(64)))
        right_i64_ptr = builder.bitcast(right_data, ir.PointerType(ir.IntType(64)))
        left_val = builder.load(left_i64_ptr)
        right_val = builder.load(right_i64_ptr)

        # Add values with overflow detection
        overflow_result = builder.call(self.sadd_overflow, [left_val, right_val])

        # Extract sum and overflow flag
        sum_val = builder.extract_value(overflow_result, 0)
        overflow_flag = builder.extract_value(overflow_result, 1)

        # Check for overflow
        overflow_block = self.pyobj_add.append_basic_block("overflow")
        success_block = self.pyobj_add.append_basic_block("success")
        builder.cbranch(overflow_flag, overflow_block, success_block)

        # Overflow case - print error and exit
        builder.position_at_end(overflow_block)
        error_msg = self._create_global_string_with_builder(
            "Error: Integer overflow in addition\n", builder
        )
        builder.call(self.printf, [error_msg])

        # Exit with error code 1
        exit_ty = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])
        exit_func = ir.Function(self.module, exit_ty, name="exit")
        builder.call(exit_func, [ir.Constant(ir.IntType(32), 1)])
        builder.unreachable()

        # Success case - return result
        builder.position_at_end(success_block)
        result_obj = builder.call(self.create_int, [sum_val])
        builder.ret(result_obj)

        # Error case - return null for now
        builder.position_at_end(error_block)
        builder.ret(ir.Constant(ir.PointerType(self.pyobj.pyobj_type), None))

        # Create print function for PyObjects
        self._create_pyobj_print()

    def _create_pyobj_print(self):
        """Create PyObject print function."""

        print_ty = ir.FunctionType(
            ir.VoidType(), [ir.PointerType(self.pyobj.pyobj_type)]
        )
        self.pyobj_print = ir.Function(self.module, print_ty, name="pyobj_print")

        entry_block = self.pyobj_print.append_basic_block("entry")
        int_block = self.pyobj_print.append_basic_block("print_int")
        str_block = self.pyobj_print.append_basic_block("print_str")
        default_block = self.pyobj_print.append_basic_block("default")

        builder = ir.IRBuilder(entry_block)

        obj = self.pyobj_print.args[0]

        # Get type tag
        tag_ptr = builder.gep(
            obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        tag = builder.load(tag_ptr)

        # Switch on type tag
        switch = builder.switch(tag, default_block)
        switch.add_case(ir.Constant(ir.IntType(32), 0), int_block)  # int
        switch.add_case(ir.Constant(ir.IntType(32), 2), str_block)  # str

        # Print integer
        builder.position_at_end(int_block)
        data_ptr = builder.gep(
            obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        data = builder.load(data_ptr)
        i64_ptr = builder.bitcast(data, ir.PointerType(ir.IntType(64)))
        val = builder.load(i64_ptr)

        # Create format string for integer (use %ld for signed)
        int_fmt = self._create_global_string_with_builder("%ld", builder)
        builder.call(self.printf, [int_fmt, val])
        builder.ret_void()

        # Print string
        builder.position_at_end(str_block)
        data_ptr = builder.gep(
            obj, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        data = builder.load(data_ptr)
        str_struct = builder.bitcast(data, ir.PointerType(self.pyobj.string_type))
        chars_ptr_ptr = builder.gep(
            str_struct, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        chars_ptr = builder.load(chars_ptr_ptr)

        str_fmt = self._create_global_string_with_builder("%s", builder)
        builder.call(self.printf, [str_fmt, chars_ptr])
        builder.ret_void()

        # Default case
        builder.position_at_end(default_block)
        unknown_fmt = self._create_global_string_with_builder(
            "<unknown object>", builder
        )
        builder.call(self.printf, [unknown_fmt])
        builder.ret_void()

    def _create_comparison_operations(self):
        """Create PyObject comparison operations."""

        # PyObject* pyobj_le(PyObject* left, PyObject* right) - less than or equal
        le_ty = ir.FunctionType(
            ir.PointerType(self.pyobj.pyobj_type),
            [
                ir.PointerType(self.pyobj.pyobj_type),
                ir.PointerType(self.pyobj.pyobj_type),
            ],
        )
        self.pyobj_le = ir.Function(self.module, le_ty, name="pyobj_le")

        block = self.pyobj_le.append_basic_block("entry")
        builder = ir.IRBuilder(block)

        left, right = self.pyobj_le.args

        # Get type tags
        left_tag_ptr = builder.gep(
            left, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        right_tag_ptr = builder.gep(
            right, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        left_tag = builder.load(left_tag_ptr)
        right_tag = builder.load(right_tag_ptr)

        # Check if both are integers (tag == 0)
        both_int_cond = builder.and_(
            builder.icmp_signed("==", left_tag, ir.Constant(ir.IntType(32), 0)),
            builder.icmp_signed("==", right_tag, ir.Constant(ir.IntType(32), 0)),
        )

        int_block = self.pyobj_le.append_basic_block("int_le")
        error_block = self.pyobj_le.append_basic_block("error")
        builder.cbranch(both_int_cond, int_block, error_block)

        # Integer comparison
        builder.position_at_end(int_block)

        # Get integer values
        left_data_ptr = builder.gep(
            left, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        right_data_ptr = builder.gep(
            right, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        left_data = builder.load(left_data_ptr)
        right_data = builder.load(right_data_ptr)
        left_i64_ptr = builder.bitcast(left_data, ir.PointerType(ir.IntType(64)))
        right_i64_ptr = builder.bitcast(right_data, ir.PointerType(ir.IntType(64)))
        left_val = builder.load(left_i64_ptr)
        right_val = builder.load(right_i64_ptr)

        # Compare values (left <= right)
        result_bool = builder.icmp_signed("<=", left_val, right_val)
        result_int = builder.zext(result_bool, ir.IntType(64))
        result_obj = builder.call(self.create_int, [result_int])
        builder.ret(result_obj)

        # Error case - return null for now
        builder.position_at_end(error_block)
        builder.ret(ir.Constant(ir.PointerType(self.pyobj.pyobj_type), None))

    def _create_less_than_comparison(self, left: ir.Value, right: ir.Value) -> ir.Value:
        """Create less than comparison for loop conditions."""
        # Similar to pyobj_le but for < instead of <=
        # For simplicity, inline the comparison here

        # Get integer values
        left_data_ptr = self.current_builder.gep(
            left, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        right_data_ptr = self.current_builder.gep(
            right, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        left_data = self.current_builder.load(left_data_ptr)
        right_data = self.current_builder.load(right_data_ptr)
        left_i64_ptr = self.current_builder.bitcast(
            left_data, ir.PointerType(ir.IntType(64))
        )
        right_i64_ptr = self.current_builder.bitcast(
            right_data, ir.PointerType(ir.IntType(64))
        )
        left_val = self.current_builder.load(left_i64_ptr)
        right_val = self.current_builder.load(right_i64_ptr)

        # Compare values (left < right)
        result_bool = self.current_builder.icmp_signed("<", left_val, right_val)
        result_int = self.current_builder.zext(result_bool, ir.IntType(64))
        return self.current_builder.call(self.create_int, [result_int])

    def _create_unary_minus(self, operand: ir.Value) -> ir.Value:
        """Create unary minus operation for PyObject."""
        # Check if operand is an integer
        tag_ptr = self.current_builder.gep(
            operand, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)]
        )
        tag = self.current_builder.load(tag_ptr)

        # Check if it's an integer (tag == 0)
        is_int_cond = self.current_builder.icmp_signed(
            "==", tag, ir.Constant(ir.IntType(32), 0)
        )

        int_block = self.current_function.append_basic_block("unary_minus_int")
        error_block = self.current_function.append_basic_block("unary_minus_error")
        self.current_builder.cbranch(is_int_cond, int_block, error_block)

        # Integer negation
        self.current_builder.position_at_end(int_block)
        data_ptr = self.current_builder.gep(
            operand, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)]
        )
        data = self.current_builder.load(data_ptr)
        i64_ptr = self.current_builder.bitcast(data, ir.PointerType(ir.IntType(64)))
        val = self.current_builder.load(i64_ptr)

        # Negate the value
        neg_val = self.current_builder.sub(ir.Constant(ir.IntType(64), 0), val)
        result_obj = self.current_builder.call(self.create_int, [neg_val])

        # We need to merge the blocks
        merge_block = self.current_function.append_basic_block("unary_minus_merge")
        self.current_builder.branch(merge_block)

        # Error case
        self.current_builder.position_at_end(error_block)
        null_result = ir.Constant(ir.PointerType(self.pyobj.pyobj_type), None)
        self.current_builder.branch(merge_block)

        # Merge block with PHI node
        self.current_builder.position_at_end(merge_block)
        phi = self.current_builder.phi(ir.PointerType(self.pyobj.pyobj_type))
        phi.add_incoming(result_obj, int_block)
        phi.add_incoming(null_result, error_block)

        return phi

    def _create_overflow_intrinsics(self):
        """Create LLVM overflow detection intrinsics."""

        # llvm.sadd.with.overflow.i64 - signed add with overflow detection
        overflow_ty = ir.LiteralStructType([ir.IntType(64), ir.IntType(1)])  # {i64, i1}
        sadd_overflow_ty = ir.FunctionType(
            overflow_ty, [ir.IntType(64), ir.IntType(64)]
        )
        self.sadd_overflow = ir.Function(
            self.module, sadd_overflow_ty, name="llvm.sadd.with.overflow.i64"
        )

    def _create_global_string(self, string_content: str) -> ir.Value:
        """Create a global string constant."""
        return self._create_global_string_with_builder(
            string_content, self.current_builder
        )

    def _create_global_string_with_builder(
        self, string_content: str, builder: ir.IRBuilder
    ) -> ir.Value:
        """Create a global string constant with a specific builder."""
        string_bytes = bytearray((string_content + "\0").encode("utf-8"))
        string_type = ir.ArrayType(ir.IntType(8), len(string_bytes))

        # Create global variable
        global_str = ir.GlobalVariable(
            self.module, string_type, name=f"str_{len(self.module.globals)}"
        )
        global_str.global_constant = True
        global_str.initializer = ir.Constant(string_type, string_bytes)

        # Get pointer to first character
        zero = ir.Constant(ir.IntType(32), 0)
        return builder.gep(global_str, [zero, zero])

    def convert(self, ir_json: str) -> str:
        """Convert Silu IR JSON to LLVM IR."""

        # Parse JSON
        try:
            ir_data = parse_ir_from_json_string(ir_json)
        except IRParseError as e:
            raise ValueError(f"Failed to parse IR: {e}")

        # First pass: collect function definitions
        self._collect_function_defs(ir_data)

        # Second pass: create function declarations
        self._create_function_declarations()

        # Create main function
        main_ty = ir.FunctionType(ir.IntType(32), [])
        main_func = ir.Function(self.module, main_ty, name="main")
        self.current_function = main_func

        entry_block = main_func.append_basic_block("entry")
        self.current_builder = ir.IRBuilder(entry_block)

        # Convert IR (skip function definitions in main)
        self._convert_node(ir_data, skip_func_defs=True)

        # Return 0 from main
        self.current_builder.ret(ir.Constant(ir.IntType(32), 0))

        # Generate function bodies
        self._generate_function_bodies()

        return str(self.module)

    def _collect_function_defs(self, node):
        """Collect function definitions from IR tree."""
        if isinstance(node, list) and len(node) > 0:
            if node[0] == "module" and len(node) > 1:
                for stmt in node[1]:
                    self._collect_function_defs(stmt)
            elif node[0] == "func_def" and len(node) >= 4:
                func_name = node[1]
                self.function_defs[func_name] = node
            else:
                # Recursively process other nodes
                for item in node[1:]:
                    if isinstance(item, list):
                        self._collect_function_defs(item)

    def _create_function_declarations(self):
        """Create LLVM function declarations for user-defined functions."""
        for func_name, func_def in self.function_defs.items():
            # All functions return PyObject* and take PyObject* parameters
            param_count = len(func_def[2]) if len(func_def) > 2 else 0
            param_types = [ir.PointerType(self.pyobj.pyobj_type)] * param_count
            func_ty = ir.FunctionType(
                ir.PointerType(self.pyobj.pyobj_type), param_types
            )
            func = ir.Function(self.module, func_ty, name=func_name)
            self.functions[func_name] = func

    def _generate_function_bodies(self):
        """Generate function bodies for user-defined functions."""
        for func_name, func_def in self.function_defs.items():
            func = self.functions[func_name]
            self._generate_function_body(func, func_def)

    def _convert_node(
        self, node: Any, skip_func_defs: bool = False
    ) -> Optional[ir.Value]:
        """Convert a single IR node."""

        if not isinstance(node, list) or len(node) == 0:
            return None

        op = node[0]

        if op == "module":
            # Convert all statements in module
            statements = node[1] if len(node) > 1 else []
            for stmt in statements:
                self._convert_node(stmt, skip_func_defs)
            return None

        elif op == "const":
            value = node[1]
            if isinstance(value, int):
                return self.current_builder.call(
                    self.create_int, [ir.Constant(ir.IntType(64), value)]
                )
            elif isinstance(value, str):
                # Create string constant
                str_len = len(value)  # Not including null terminator
                str_ptr = self._create_global_string(value)
                return self.current_builder.call(
                    self.create_str, [str_ptr, ir.Constant(ir.IntType(32), str_len)]
                )
            else:
                # For now, just treat other constants as integers
                return self.current_builder.call(
                    self.create_int, [ir.Constant(ir.IntType(64), 0)]
                )

        elif op == "name":
            var_name = node[1]
            if var_name in self.variables:
                # Load the value from the alloca
                return self.current_builder.load(self.variables[var_name])
            else:
                # Return a null PyObject for undefined variables
                return ir.Constant(ir.PointerType(self.pyobj.pyobj_type), None)

        elif op == "assign":
            target = node[1]
            value_node = node[2]
            value = self._convert_node(value_node)
            if value and isinstance(target, str):
                # Create alloca if variable doesn't exist
                if target not in self.variables:
                    self.variables[target] = self.current_builder.alloca(
                        ir.PointerType(self.pyobj.pyobj_type), name=target
                    )
                # Store the value
                self.current_builder.store(value, self.variables[target])
            return value

        elif op == "+":
            if len(node) >= 3:
                left = self._convert_node(node[1])
                right = self._convert_node(node[2])
                if left and right:
                    return self.current_builder.call(self.pyobj_add, [left, right])
            return None

        elif op == "-":
            if len(node) == 2:
                # Unary minus: -operand
                operand = self._convert_node(node[1])
                if operand:
                    return self._create_unary_minus(operand)
            elif len(node) >= 3:
                # Binary minus: left - right (not implemented yet)
                # For now, just ignore binary subtraction
                pass
            return None

        elif op == "<=":
            if len(node) >= 3:
                left = self._convert_node(node[1])
                right = self._convert_node(node[2])
                if left and right:
                    return self.current_builder.call(self.pyobj_le, [left, right])
            return None

        elif op == "call":
            func_node = node[1]
            args_node = node[2] if len(node) > 2 else []

            if (
                isinstance(func_node, list)
                and len(func_node) >= 2
                and func_node[0] == "name"
            ):
                func_name = func_node[1]

                if func_name == "print":
                    # Handle print function
                    if args_node:
                        for arg_node in args_node:
                            arg_val = self._convert_node(arg_node)
                            if arg_val:
                                self.current_builder.call(self.pyobj_print, [arg_val])
                    # Add newline
                    newline_fmt = self._create_global_string("\n")
                    self.current_builder.call(self.printf, [newline_fmt])
                    return None

                elif func_name == "range":
                    # Handle range function with start and stop parameters
                    if len(args_node) == 1:
                        # range(stop) -> return stop
                        return self._convert_node(args_node[0])
                    elif len(args_node) >= 2:
                        # range(start, stop) -> return stop for loop iteration count
                        # For proper loop implementation, we need the stop value
                        stop_val = self._convert_node(args_node[1])
                        return (
                            stop_val
                            if stop_val
                            else self.current_builder.call(
                                self.create_int, [ir.Constant(ir.IntType(64), 0)]
                            )
                        )
                    return self.current_builder.call(
                        self.create_int, [ir.Constant(ir.IntType(64), 0)]
                    )

                elif func_name in self.functions:
                    # Handle user-defined function calls
                    func = self.functions[func_name]
                    llvm_args = []
                    for arg_node in args_node:
                        arg_val = self._convert_node(arg_node)
                        if arg_val:
                            llvm_args.append(arg_val)

                    if len(llvm_args) == len(func.args):
                        return self.current_builder.call(func, llvm_args)
                    else:
                        # Argument count mismatch - return null for now
                        return ir.Constant(ir.PointerType(self.pyobj.pyobj_type), None)

            return None

        elif op == "if":
            if len(node) >= 4:
                test_node = node[1]
                body_stmts = node[2]
                else_stmts = node[3]

                # Evaluate condition
                test_val = self._convert_node(test_node)
                if test_val:
                    # Create basic blocks for if/else/merge
                    then_block = self.current_function.append_basic_block("if_then")
                    else_block = self.current_function.append_basic_block("if_else")
                    merge_block = self.current_function.append_basic_block("if_merge")

                    # Extract boolean value from PyObject and branch accordingly
                    # Get the data pointer (should be i64 for integers)
                    data_ptr = self.current_builder.gep(
                        test_val,
                        [
                            ir.Constant(ir.IntType(32), 0),
                            ir.Constant(ir.IntType(32), 1),
                        ],
                    )
                    data = self.current_builder.load(data_ptr)
                    i64_ptr = self.current_builder.bitcast(
                        data, ir.PointerType(ir.IntType(64))
                    )
                    bool_val = self.current_builder.load(i64_ptr)

                    # Convert i64 to i1 (boolean) - non-zero is true
                    condition = self.current_builder.icmp_signed(
                        "!=", bool_val, ir.Constant(ir.IntType(64), 0)
                    )
                    self.current_builder.cbranch(condition, then_block, else_block)

                    # Generate then block
                    self.current_builder.position_at_end(then_block)
                    for stmt in body_stmts:
                        self._convert_node(stmt)
                        if self.current_builder.block.is_terminated:
                            break
                    if not self.current_builder.block.is_terminated:
                        self.current_builder.branch(merge_block)

                    # Generate else block
                    self.current_builder.position_at_end(else_block)
                    for stmt in else_stmts:
                        self._convert_node(stmt)
                        if self.current_builder.block.is_terminated:
                            break
                    if not self.current_builder.block.is_terminated:
                        self.current_builder.branch(merge_block)

                    # Continue with merge block
                    self.current_builder.position_at_end(merge_block)

                return None

        elif op == "for":
            if len(node) >= 4:
                target_node = node[1]
                iter_node = node[2]
                body_stmts = node[3]

                # Enhanced for loop implementation with proper range handling
                # Handle range() call to get start and stop values
                start_val = None
                end_val = None

                if (
                    isinstance(iter_node, list)
                    and len(iter_node) >= 3
                    and iter_node[0] == "call"
                ):
                    func_node = iter_node[1]
                    args_node = iter_node[2] if len(iter_node) > 2 else []

                    if (
                        isinstance(func_node, list)
                        and len(func_node) >= 2
                        and func_node[0] == "name"
                        and func_node[1] == "range"
                    ):
                        if len(args_node) == 1:
                            # range(stop) -> start=0, stop=args[0]
                            start_val = self.current_builder.call(
                                self.create_int, [ir.Constant(ir.IntType(64), 0)]
                            )
                            end_val = self._convert_node(args_node[0])
                        elif len(args_node) >= 2:
                            # range(start, stop) -> start=args[0], stop=args[1]
                            start_val = self._convert_node(args_node[0])
                            end_val = self._convert_node(args_node[1])

                # Default values if not range()
                if not start_val:
                    start_val = self.current_builder.call(
                        self.create_int, [ir.Constant(ir.IntType(64), 0)]
                    )
                if not end_val:
                    end_val = self._convert_node(
                        iter_node
                    ) or self.current_builder.call(
                        self.create_int, [ir.Constant(ir.IntType(64), 10)]
                    )

                # Create loop blocks
                loop_init = self.current_function.append_basic_block("loop_init")
                loop_cond = self.current_function.append_basic_block("loop_cond")
                loop_body = self.current_function.append_basic_block("loop_body")
                loop_end = self.current_function.append_basic_block("loop_end")

                # Jump to init
                self.current_builder.branch(loop_init)

                # Initialize loop variable to start value
                self.current_builder.position_at_end(loop_init)
                counter_ptr = self.current_builder.alloca(
                    ir.PointerType(self.pyobj.pyobj_type)
                )
                self.current_builder.store(start_val, counter_ptr)
                self.current_builder.branch(loop_cond)

                # Loop condition: counter < end_val (for proper range semantics)
                self.current_builder.position_at_end(loop_cond)
                current_val = self.current_builder.load(counter_ptr)

                # Use < instead of <= for proper range semantics
                cond_result = self._create_less_than_comparison(current_val, end_val)

                # Extract boolean condition
                data_ptr = self.current_builder.gep(
                    cond_result,
                    [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 1)],
                )
                data = self.current_builder.load(data_ptr)
                i64_ptr = self.current_builder.bitcast(
                    data, ir.PointerType(ir.IntType(64))
                )
                bool_val = self.current_builder.load(i64_ptr)
                condition = self.current_builder.icmp_signed(
                    "!=", bool_val, ir.Constant(ir.IntType(64), 0)
                )
                self.current_builder.cbranch(condition, loop_body, loop_end)

                # Loop body
                self.current_builder.position_at_end(loop_body)

                # Set loop variable if it's a name (current iteration value)
                if (
                    isinstance(target_node, list)
                    and len(target_node) >= 2
                    and target_node[0] == "name"
                ):
                    var_name = target_node[1]
                    # Create alloca if variable doesn't exist
                    if var_name not in self.variables:
                        self.variables[var_name] = self.current_builder.alloca(
                            ir.PointerType(self.pyobj.pyobj_type), name=var_name
                        )
                    # Store current iteration value
                    current_iter_val = self.current_builder.load(counter_ptr)
                    self.current_builder.store(
                        current_iter_val, self.variables[var_name]
                    )

                # Execute body statements
                for stmt in body_stmts:
                    self._convert_node(stmt)
                    if self.current_builder.block.is_terminated:
                        break

                # Increment counter if not terminated
                if not self.current_builder.block.is_terminated:
                    current_counter = self.current_builder.load(counter_ptr)
                    one = self.current_builder.call(
                        self.create_int, [ir.Constant(ir.IntType(64), 1)]
                    )
                    next_val = self.current_builder.call(
                        self.pyobj_add, [current_counter, one]
                    )
                    self.current_builder.store(next_val, counter_ptr)
                    self.current_builder.branch(loop_cond)

                # Continue after loop
                self.current_builder.position_at_end(loop_end)
                return None

        elif op == "func_def":
            # Function definitions are handled separately
            if skip_func_defs:
                return None
            # This shouldn't be reached in normal flow
            return None

        elif op == "tuple_assign":
            # Handle tuple unpacking assignment: a, b = expr
            if len(node) >= 3:
                targets = node[1]  # List of target variable names
                value_node = node[2]  # Expression to unpack

                # Handle tuple assignment with proper simultaneous semantics
                if (
                    isinstance(value_node, list)
                    and len(value_node) >= 2
                    and value_node[0] == "tuple"
                ):
                    elements = value_node[1] if len(value_node) > 1 else []

                    # First, evaluate all right-hand side values before any assignment
                    # This ensures simultaneous assignment semantics for cases like a, b = b, a + b
                    evaluated_values = []
                    for element in elements:
                        element_val = self._convert_node(element)
                        evaluated_values.append(element_val)

                    # Then assign all values to targets
                    for i, target in enumerate(targets):
                        if (
                            i < len(evaluated_values)
                            and evaluated_values[i]
                            and isinstance(target, str)
                        ):
                            # Create alloca if variable doesn't exist
                            if target not in self.variables:
                                self.variables[target] = self.current_builder.alloca(
                                    ir.PointerType(self.pyobj.pyobj_type), name=target
                                )
                            # Store the value
                            self.current_builder.store(
                                evaluated_values[i], self.variables[target]
                            )

                return None

        elif op == "tuple":
            # Handle tuple creation
            if len(node) >= 2:
                elements = node[1]
                # For now, just return the first element
                # A full implementation would create a tuple object
                if elements:
                    return self._convert_node(elements[0])
            return None

        elif op == "return":
            # Handle return statements
            if len(node) > 1:
                return_val = self._convert_node(node[1])
                if (
                    return_val
                    and self.current_function
                    and not self.current_builder.block.is_terminated
                ):
                    self.current_builder.ret(return_val)
                    return return_val
            # Return None/null if no value
            null_val = ir.Constant(ir.PointerType(self.pyobj.pyobj_type), None)
            if self.current_function and not self.current_builder.block.is_terminated:
                self.current_builder.ret(null_val)
            return null_val

        else:
            # Ignore unknown operations for now
            return None

    def _generate_function_body(self, func: ir.Function, func_def: Any):
        """Generate the body of a user-defined function."""
        if len(func_def) < 4:
            return

        # func_name = func_def[1]
        param_names = func_def[2]
        body_stmts = func_def[3]

        # Create function entry block
        entry_block = func.append_basic_block("entry")

        # Save current state
        old_function = self.current_function
        old_builder = self.current_builder
        old_variables = self.variables.copy()

        # Set up function context
        self.current_function = func
        self.current_builder = ir.IRBuilder(entry_block)

        # Set up parameters as variables
        for i, param_name in enumerate(param_names):
            if i < len(func.args):
                # Create alloca for parameter and store the argument value
                param_alloca = self.current_builder.alloca(
                    ir.PointerType(self.pyobj.pyobj_type), name=param_name
                )
                self.current_builder.store(func.args[i], param_alloca)
                self.variables[param_name] = param_alloca

        # Generate function body
        return_generated = False
        for stmt in body_stmts:
            # result =
            self._convert_node(stmt)
            if isinstance(stmt, list) and len(stmt) > 0 and stmt[0] == "return":
                return_generated = True
                break

        # Add default return if no explicit return
        if not return_generated and not self.current_builder.block.is_terminated:
            null_val = ir.Constant(ir.PointerType(self.pyobj.pyobj_type), None)
            self.current_builder.ret(null_val)

        # Restore previous state
        self.current_function = old_function
        self.current_builder = old_builder
        self.variables = old_variables

    def save_to_file(self, llvm_ir: str, filename: str):
        """Save LLVM IR to file."""
        with open(filename, "w") as f:
            f.write(llvm_ir)


def main():
    """Command line interface for Silu IR to LLVM converter."""

    if len(sys.argv) != 3:
        print("Usage: python silu_ir_to_llvm.py <input.ir.json> <output.ll>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        # Read Silu IR
        with open(input_file, "r", encoding="utf-8") as f:
            ir_json = f.read()

        # Convert to LLVM IR
        converter = SiluToLLVMConverter()
        llvm_ir = converter.convert(ir_json)

        # Save result
        converter.save_to_file(llvm_ir, output_file)

        print(f"Successfully converted {input_file} to {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
