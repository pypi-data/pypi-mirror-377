from typing import Any, Dict
from .ir_utils import parse_ir_from_file
from .symbolic_executor import SymbolicExecutor
from .symbolic_utils import logger, Config


def execute_symbolic_from_file_with_executor(
    file_path: str,
    performance_mode: bool = False,
    debug: bool = False,
) -> Dict[str, Any]:
    """Execute symbolic analysis from an IR file and return paths with function analyses"""
    try:
        ir_program = parse_ir_from_file(file_path, encoding=Config.DEFAULT_ENCODING)

        executor = SymbolicExecutor(
            performance_mode=performance_mode,
            debug=debug,
        )
        try:
            paths = executor.execute_program(ir_program)
            result = {"paths": paths}
            if hasattr(executor, "function_analyses") and executor.function_analyses:
                result["function_analyses"] = executor.function_analyses

            return result
        except KeyError as ke:
            logger.error(f"KeyError in symbolic execution: {ke}")
            # Raise RuntimeError for test compatibility while providing error info
            raise RuntimeError(f"KeyError in symbolic execution: {ke}")
    except Exception as e:
        logger.error(f"Error in symbolic execution from file '{file_path}': {e}")
        # import traceback
        # logger.error(traceback.format_exc())
        # Raise RuntimeError for compatibility with tests
        raise RuntimeError(f"Error in symbolic execution from file '{file_path}': {e}")
