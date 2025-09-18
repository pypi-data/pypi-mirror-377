#!/usr/bin/env python3
"""
Command line interface for the Silu interpreter and IR generator.
"""

import argparse
import ast
import json
import sys
import logging
from pathlib import Path
from typing import Any

from silu.interpreter import SiluInterpreter
from silu.ir_generator import SiluIRGenerator
from silu.ir_interpreter import (
    execute_ir_from_file,
    execute_ir_from_string,
)
from silu.symbolic_executor import (
    SymbolicExecutor,
    # execute_symbolic_from_string_with_executor,
    #     execute_symbolic_from_file,
    #     execute_symbolic_from_string,
)
from silu.symbolic_executor_wrapper import execute_symbolic_from_file_with_executor

from silu.ir_to_source import convert_ir_file_to_source, convert_ir_string_to_source

try:
    from .silu_ir_to_llvm import SiluToLLVMConverter

    LLVM_AVAILABLE = True
except ImportError:
    LLVM_AVAILABLE = False

# Setup logging
logger = logging.getLogger(__name__)


def read_source_file(file_path: str) -> str:
    """Read source code from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def format_ir_output(ir_result: Any, output_format: str) -> str:
    """Format IR result according to the specified output format."""
    if output_format == "json":
        return json.dumps(ir_result, indent=2, default=str)
    elif output_format == "pretty":
        import pprint

        return pprint.pformat(ir_result, width=80, depth=None)
    elif output_format == "compact":
        return str(ir_result)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def run_interpreter(source_code: str, **kwargs) -> None:
    """Run the interpreter on the source code."""
    try:
        tree = ast.parse(source_code)
        interpreter = SiluInterpreter(**kwargs)
        interpreter.visit(tree)
    except SyntaxError as e:
        print(f"Syntax Error: {e}", file=sys.stderr)
        sys.exit(1)
    except AttributeError as e:
        # Special handling for _fields attribute error which occurs with classes
        # if "'ClassType' object has no attribute '_fields'" in str(e) or "'dict' object has no attribute '_fields'" in str(e):
        #     print("Note: Class feature partially implemented, some operations may not work", file=sys.stderr)
        #     sys.exit(1)
        print(f"Runtime Error: {e}", file=sys.stderr)

        if kwargs.get("debug", False):
            import traceback

            logger.error(traceback.format_exc())

        sys.exit(1)
    except Exception as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)


def check_interpreter(source_code: str, **kwargs) -> tuple[bool, str]:
    """Check if the source code can be interpreted by Silu without errors.

    Returns:
        tuple[bool, str]: (success, error_reason) where success is True if the code
        can be interpreted successfully, and error_reason is a description of the failure.
    """
    import io
    import contextlib

    try:
        tree = ast.parse(source_code)
        interpreter = SiluInterpreter(**kwargs)

        # Suppress all output during interpretation
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            interpreter.visit(tree)

        return True, ""
    except SyntaxError as e:
        return False, f"syntax error: {e.msg} at line {e.lineno}"
    except NotImplementedError as e:
        return False, f"unsupported feature: {str(e)}"
    except AttributeError as e:
        error_msg = str(e)
        if "has no attribute" in error_msg:
            return False, f"unsupported operation: {error_msg}"
        return False, f"attribute error: {error_msg}"
    except NameError as e:
        return False, f"name error: {str(e)}"
    except TypeError as e:
        return False, f"type error: {str(e)}"
    except ValueError as e:
        return False, f"value error: {str(e)}"
    except ZeroDivisionError:
        return False, "runtime error: division by zero"
    except IndexError as e:
        return False, f"index error: {str(e)}"
    except KeyError as e:
        return False, f"key error: {str(e)}"
    except Exception as e:
        # Generic catch-all for other errors
        error_type = type(e).__name__
        return False, f"{error_type.lower()}: {str(e)}"


def run_check(filename: str) -> None:
    """Check if a file can be interpreted by Silu and print result."""
    try:
        # Read file directly without using read_source_file to avoid sys.exit
        with open(filename, "r", encoding="utf-8") as file:
            source_code = file.read()

        if not source_code.strip():
            print(f"{filename} bad: empty file")
            return

        success, error_reason = check_interpreter(source_code)
        if success:
            print(f"{filename} ok")
        else:
            print(f"{filename} bad: {error_reason}")
    except FileNotFoundError:
        print(f"{filename} bad: file not found")
    except PermissionError:
        print(f"{filename} bad: permission denied")
    except UnicodeDecodeError:
        print(f"{filename} bad: file encoding error")
    except Exception as e:
        print(f"{filename} bad: {str(e)}")


def generate_ir(source_code: str, output_format: str = "pretty", **kwargs) -> None:
    """Generate IR from source code and print it."""
    try:
        tree = ast.parse(source_code)
        ir_generator = SiluIRGenerator(**kwargs)
        ir_result = ir_generator.visit(tree)

        formatted_output = format_ir_output(ir_result, output_format)
        print(formatted_output)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating IR: {e}", file=sys.stderr)
        sys.exit(1)


def run_ir_interpreter(ir_source: str, **kwargs) -> None:
    """Run the IR interpreter on IR code."""
    try:
        result = None
        if ir_source.strip().startswith(("[", "(")):
            # Direct IR string
            result = execute_ir_from_string(ir_source)
        else:
            # Treat as filename
            result = execute_ir_from_file(ir_source)

        if result is not None:
            print(result)
    except Exception as e:
        print(f"Error executing IR: {e}", file=sys.stderr)
        sys.exit(1)


def save_ir_to_file(ir_result: Any, output_file: str, output_format: str) -> None:
    """Save IR result to a file."""
    try:
        formatted_output = format_ir_output(ir_result, output_format)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print(f"IR saved to: {output_file}")
    except IOError as e:
        print(f"Error writing to file '{output_file}': {e}", file=sys.stderr)
        sys.exit(1)


def run_llvm_ir_generator(
    source: str, output_file: str = None, is_file: bool = True, **kwargs
) -> None:
    """Generate LLVM IR from Silu IR."""
    if not LLVM_AVAILABLE:
        print(
            "Error: LLVM IR generation not available. Please install llvmlite.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        if is_file:
            # Read IR from file
            with open(source, "r", encoding="utf-8") as f:
                ir_json = f.read()
        else:
            # Use IR string directly
            ir_json = source

        # Convert to LLVM IR
        converter = SiluToLLVMConverter()
        llvm_ir = converter.convert(ir_json)

        if output_file:
            converter.save_to_file(llvm_ir, output_file)
            print(f"LLVM IR saved to: {output_file}")
        else:
            print(llvm_ir)

    except Exception as e:
        print(f"Error generating LLVM IR: {e}", file=sys.stderr)
        sys.exit(1)


def run_ir_to_source_converter(
    ir_source: str, output_file: str = None, **kwargs
) -> None:
    """Convert IR to source code."""
    try:
        if ir_source.strip().startswith(("[", "(")):
            # Direct IR string
            source_code = convert_ir_string_to_source(ir_source)
        else:
            # Treat as filename
            source_code = convert_ir_file_to_source(ir_source, output_file)

        if not output_file:
            print(source_code)
        else:
            print(f"Source code saved to: {output_file}")

    except Exception as e:
        print(f"Error converting IR to source: {e}", file=sys.stderr)
        sys.exit(1)


def run_symbolic_executor(source: str, is_file: bool = True, **kwargs) -> dict[str, Any]:
    """Run symbolic execution on source code or IR."""
    debug = kwargs.get("debug", False)
    report = {}
    try:
        performance_mode = kwargs.get("performance_mode", False)
        if debug:
            logger.info(
                f"Running symbolic execution on {'file' if is_file else 'source'}: {source}"
            )

        simplify = kwargs.get("simplify", False)
        solve = kwargs.get("solve", False)

        executor = SymbolicExecutor(
            performance_mode=performance_mode,
            debug=debug,
        )

        if is_file:
            # Execute from file
            if source.endswith(".si"):
                # Silu source file - need to convert to IR first
                # TODO
                source_code = read_source_file(source)
                tree = ast.parse(source_code)
                ir_generator = SiluIRGenerator()
                ir_result = ir_generator.visit(tree)
                paths = executor.execute_program(ir_result)
            else:
                # IR file - need to get both paths and function analyses
                ir_executor_result = execute_symbolic_from_file_with_executor(
                    source,
                    performance_mode=performance_mode,
                    debug=debug,
                )
                paths = ir_executor_result.get("paths", [])

                # Handle error in symbolic execution
                if "error" in ir_executor_result:
                    logger.warning(
                        f"Symbolic execution had errors: {ir_executor_result['error']}"
                    )

                # Transfer function analyses from IR executor to main executor
                if "function_analyses" in ir_executor_result:
                    executor.function_analyses = ir_executor_result["function_analyses"]

        else:
            raise ValueError("Invalid input source")
            # Execute from IR string
            # if source.strip().startswith(("[", "(")):
            #     # IR string
            #     ir_executor_result = execute_symbolic_from_string_with_executor(
            #         source,
            #         performance_mode=performance_mode,
            #         debug=debug,
            #     )
            #     paths = ir_executor_result["paths"]
            #     # Transfer function analyses from IR executor to main executor
            #     if "function_analyses" in ir_executor_result:
            #         executor.function_analyses = ir_executor_result["function_analyses"]
            # else:
            #     # Silu source string - convert to IR first
            #     tree = ast.parse(source)
            #     ir_generator = SiluIRGenerator()
            #     ir_result = ir_generator.visit(tree)
            #     paths = executor.execute_program(ir_result)

        # Apply condition simplification if requested
        if simplify:
            if paths:
                paths = executor.simplify_path_conditions(paths)

            # Also simplify function analysis results
            if hasattr(executor, "function_analyses"):
                for func_name, func_paths in executor.function_analyses.items():
                    executor.function_analyses[func_name] = (
                        executor.simplify_path_conditions(func_paths)
                    )

        # Generate and display unified report with optional test cases
        if paths:
            # Enhance paths with test cases if solve option is enabled
            if solve:
                # Also enhance function analyses paths
                if (
                    hasattr(executor, "function_analyses")
                    and executor.function_analyses
                ):
                    for func_name, func_paths in executor.function_analyses.items():
                        if isinstance(func_paths, list) and func_paths:
                            # Process paths before report generation
                            # for path in func_paths:
                            #     if hasattr(path, "clean_test_inputs"):
                            #         path.clean_test_inputs()
                            executor.function_analyses[func_name] = func_paths

            # Generate and print report for all files
            try:
                report = executor.generate_report(paths)
                output = kwargs.get("output", False)
                if debug or not output:
                    print(json.dumps(report, indent=2, default=str))
            except Exception as e:
                logger.error(f"Error generating report: {e}")
                print(f"Error generating report: {e}", file=sys.stderr)
                print(
                    json.dumps({"error": str(e), "paths_count": len(paths)}, indent=2)
                )
        else:
            print("No execution paths found.")
        return report
    except KeyError as ke:
        print(f"Dictionary key error in symbolic execution: {ke}", file=sys.stderr)
        if debug:
            import traceback

            logger.error(traceback.format_exc())
        print(json.dumps({"error": f"KeyError: {ke}"}, indent=2))
    except Exception as e:
        print(f"Error in symbolic execution: {e}", file=sys.stderr)
        if debug:
            import traceback

            logger.error(traceback.format_exc())
        print(json.dumps({"error": str(e)}, indent=2))
    return report

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Silu Language Processor - Interpreter, IR Generator, and IR Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interpret a Silu program (traditional usage)
  %(prog)s program.si

  # Interpret a Silu program (explicit)
  %(prog)s interpret program.si

  # Generate IR in pretty format
  %(prog)s ir program.si

  # Generate IR in JSON format
  %(prog)s ir program.si --format json

  # Save IR to file
  %(prog)s ir program.si --output program.ir.json --format json

  # Execute IR directly
  %(prog)s exec program.ir.json

  # Convert IR back to source code
  %(prog)s to-source program.ir.json

  # Convert IR to source and save to file
  %(prog)s to-source program.ir.json --output program_reconstructed.si

  # Symbolic execution of a Silu program
  %(prog)s symbolic program.si

  # Symbolic execution of IR
  %(prog)s symbolic program.ir.json

  # Process source code directly
  %(prog)s interpret --source "x = 5; print(x)"

  # Check if Python code can be interpreted by Silu
  %(prog)s check program.py
  # Output: program.py ok (or program.py bad: reason)
""",
    )

    subparsers = parser.add_subparsers(
        dest="mode", help="Processing mode", required=True
    )

    # Interpreter subcommand
    interpret_parser = subparsers.add_parser(
        "interpret", help="Interpret and execute Silu code"
    )
    interpret_parser.add_argument(
        "file", nargs="?", help="Silu source file to interpret"
    )
    interpret_parser.add_argument(
        "--source", help="Source code string to interpret (alternative to file)"
    )
    interpret_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose output"
    )

    # Check subcommand
    check_parser = subparsers.add_parser(
        "check", help="Check if Python code can be interpreted by Silu"
    )
    check_parser.add_argument("file", help="Python source file to check")

    # IR generation subcommand
    ir_parser = subparsers.add_parser("ir", help="Generate intermediate representation")
    ir_parser.add_argument("file", nargs="?", help="Silu source file to process")
    ir_parser.add_argument(
        "--source", help="Source code string to process (alternative to file)"
    )
    ir_parser.add_argument(
        "--format",
        choices=["pretty", "json", "compact"],
        default="pretty",
        help="Output format for IR (default: pretty)",
    )
    ir_parser.add_argument(
        "--output", "-o", help="Output file to save IR (default: stdout)"
    )
    ir_parser.add_argument(
        "--no-types",
        action="store_true",
        help="Disable type information recording in IR",
    )

    # IR execution subcommand
    exec_parser = subparsers.add_parser("exec", help="Execute IR directly")
    exec_parser.add_argument("file", help="IR file to execute")
    exec_parser.add_argument(
        "--source", help="IR string to execute (alternative to file)"
    )
    exec_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose output"
    )

    # IR to source conversion subcommand
    to_source_parser = subparsers.add_parser(
        "to-source", help="Convert IR to source code"
    )
    to_source_parser.add_argument("file", nargs="?", help="IR file to convert")
    to_source_parser.add_argument(
        "--source", help="IR string to convert (alternative to file)"
    )
    to_source_parser.add_argument(
        "--output", "-o", help="Output file to save source code (default: stdout)"
    )

    # LLVM IR generation subcommand
    if LLVM_AVAILABLE:
        llvm_parser = subparsers.add_parser(
            "llvm", help="Generate LLVM IR from Silu IR"
        )
        llvm_parser.add_argument("file", nargs="?", help="Silu IR file to convert")
        llvm_parser.add_argument(
            "--source", help="IR string to convert (alternative to file)"
        )
        llvm_parser.add_argument(
            "--output", "-o", help="Output file to save LLVM IR (default: stdout)"
        )

    # Symbolic execution subcommand
    symbolic_parser = subparsers.add_parser(
        "symbolic", help="Perform symbolic execution"
    )
    symbolic_parser.add_argument(
        "file", nargs="?", help="Silu source file or IR file to analyze"
    )
    symbolic_parser.add_argument(
        "--source", help="Source code or IR string to analyze (alternative to file)"
    )
    symbolic_parser.add_argument(
        "--output", "-o", help="Output file to save symbolic execution report"
    )
    symbolic_parser.add_argument(
        "--format",
        choices=["json", "pretty"],
        default="json",
        help="Output format for the report (default: json)",
    )
    symbolic_parser.add_argument(
        "--simplify",
        action="store_true",
        help="Simplify and merge path conditions where possible",
    )
    symbolic_parser.add_argument(
        "--solve",
        action="store_true",
        help="Use Z3 solver to generate concrete test cases for each execution path",
    )
    symbolic_parser.add_argument(
        "--include-function-paths",
        action="store_true",
        help="Include function internal paths in main path collection (for compatibility with original behavior)",
    )
    symbolic_parser.add_argument(
        "--performance-mode",
        action="store_true",
        help="Enable performance optimizations for faster execution with simplified analysis",
    )
    symbolic_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with verbose output"
    )

    return parser


def validate_arguments(args) -> None:
    """Validate command line arguments."""
    if args.mode == "check":
        # For check mode, only file is required (no --source support)
        if not args.file:
            print(
                "Error: A Python source file must be provided for check mode.",
                file=sys.stderr,
            )
            sys.exit(1)
        # Don't check file existence here for check mode - let run_check handle it
    elif args.mode in ["exec", "symbolic", "to-source", "llvm"]:
        # For exec/symbolic/to-source/llvm modes, either file or --source is required
        if not args.file and not args.source:
            if args.mode == "exec":
                mode_name = "IR file"
            elif args.mode == "to-source":
                mode_name = "IR file"
            elif args.mode == "llvm":
                mode_name = "IR file"
            else:
                mode_name = "source file or IR file"
            print(
                f"Error: Either a {mode_name} or --source must be provided.",
                file=sys.stderr,
            )
            sys.exit(1)
        if args.file and args.source:
            print("Error: Cannot specify both file and --source.", file=sys.stderr)
            sys.exit(1)
        if args.file and not Path(args.file).exists():
            print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
            sys.exit(1)
    else:
        # For interpret/ir modes, either file or --source is required
        if not args.file and not args.source:
            print(
                "Error: Either a source file or --source must be provided.",
                file=sys.stderr,
            )
            sys.exit(1)
        if args.file and args.source:
            print("Error: Cannot specify both file and --source.", file=sys.stderr)
            sys.exit(1)
        if args.file and not Path(args.file).exists():
            print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
            sys.exit(1)


def handle_legacy_usage(args) -> bool:
    """Handle legacy usage: silu file.si (interpret directly)."""
    # Check if it's legacy usage: exactly 2 args, second arg is not a subcommand
    if (
        len(sys.argv) == 2
        and not sys.argv[1].startswith("-")
        and sys.argv[1] not in ["interpret", "ir", "exec", "symbolic", "to-source"]
    ):
        filename = sys.argv[1]
        try:
            source_code = read_source_file(filename)
            run_interpreter(source_code)
        except KeyboardInterrupt:
            print("\nInterrupted by user.", file=sys.stderr)
            sys.exit(1)
        return True
    return False


def main() -> None:
    """Main entry point for the Silu CLI."""
    # Handle legacy usage first (backward compatibility)
    if handle_legacy_usage(sys.argv):
        return

    parser = create_parser()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # If no mode specified, show help
    if not args.mode:
        parser.print_help()
        sys.exit(1)

    # Validate arguments
    validate_arguments(args)

    # Handle check mode separately (doesn't need source code validation)
    if args.mode == "check":
        try:
            run_check(args.file)
        except KeyboardInterrupt:
            print("\nInterrupted by user.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Get source code for other modes
    if args.file:
        source_code = read_source_file(args.file)
        source_name = args.file
    else:
        source_code = args.source
        source_name = "<string>"

    if not source_code.strip():
        print("Error: Source code is empty.", file=sys.stderr)
        sys.exit(1)

    # Process based on mode
    try:
        if args.mode == "interpret":
            if hasattr(args, "debug") and args.debug:
                print(f"Interpreting {source_name} (debug mode)...", file=sys.stderr)

            run_interpreter(source_code)

        elif args.mode == "ir":
            # Prepare kwargs for IR generator
            ir_kwargs = {"record_types": not getattr(args, "no_types", False)}

            if hasattr(args, "output") and args.output:
                # Generate IR and save to file
                tree = ast.parse(source_code)
                ir_generator = SiluIRGenerator(**ir_kwargs)
                ir_result = ir_generator.visit(tree)
                save_ir_to_file(ir_result, args.output, args.format)
            else:
                # Generate IR and print to stdout
                generate_ir(source_code, args.format, **ir_kwargs)

        elif args.mode == "exec":
            # Execute IR directly
            ir_kwargs = {"debug": getattr(args, "debug", False)}

            if args.source:
                # Execute IR from command line source
                run_ir_interpreter(args.source, **ir_kwargs)
            else:
                # Execute IR from file
                run_ir_interpreter(args.file, **ir_kwargs)

        elif args.mode == "to-source":
            # IR to source conversion
            to_source_kwargs = {"output_file": getattr(args, "output", None)}

            if args.source:
                # Convert IR from command line source
                run_ir_to_source_converter(args.source, **to_source_kwargs)
            else:
                # Convert IR from file
                run_ir_to_source_converter(args.file, **to_source_kwargs)

        elif args.mode == "llvm":
            # LLVM IR generation
            llvm_kwargs = {"output_file": getattr(args, "output", None)}

            if args.source:
                # Generate LLVM IR from command line IR source
                run_llvm_ir_generator(args.source, is_file=False, **llvm_kwargs)
            else:
                # Generate LLVM IR from IR file
                run_llvm_ir_generator(args.file, is_file=True, **llvm_kwargs)

        elif args.mode == "symbolic":
            # Symbolic execution
            symbolic_kwargs = {
                "simplify": getattr(args, "simplify", False),
                "solve": getattr(args, "solve", False),
                "performance_mode": getattr(args, "performance_mode", False),
                "debug": getattr(args, "debug", False),
                "output": getattr(args, "output", False),
            }

            # Execute symbolic execution with better error handling
            report = {}
            if args.source:
                # Symbolic execution from command line source
                report = run_symbolic_executor(args.source, is_file=False, **symbolic_kwargs)
            else:
                # Symbolic execution from file
                report = run_symbolic_executor(args.file, is_file=True, **symbolic_kwargs)

            if hasattr(args, "output") and args.output:
                # Save symbolic execution report to file
                with open(args.output, "w") as f:
                    report_str = json.dumps(report, indent=2, default=str)
                    f.write(report_str)

    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", file=sys.stderr)
        # if hasattr(args, "debug") and getattr(args, "debug", False):
        #     import traceback
        #     logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
