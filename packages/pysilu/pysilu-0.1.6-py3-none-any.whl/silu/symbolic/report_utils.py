#!/usr/bin/env python3
"""
Report Generation Utilities for Symbolic Execution

This module provides utilities for generating reports and summaries from
symbolic execution results, including path analysis and test case generation.
"""

from typing import Any, Dict, List, Optional

def generate_comprehensive_report(
    paths: List[Any],
    performance_mode: bool = False,
    global_env_functions: Optional[Dict] = None,
    function_analyses: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Generate a comprehensive report of symbolic execution results with enhanced analysis

    Args:
        paths: List of execution paths
        performance_mode: Whether to generate a simplified report for performance
        global_env_functions: Global environment functions dict
        function_analyses: Function analysis results

    Returns:
        Comprehensive report dictionary
    """

    if performance_mode:
        return generate_fast_comprehensive_report(
            paths, global_env_functions, function_analyses
        )

    satisfiable_paths = [p for p in paths if getattr(p, "satisfiable", True)]
    report = {
        "total_paths": len(paths),
        "satisfiable_paths": len(satisfiable_paths),
        "paths": [path.to_dict() for path in paths],
    }

    # Add function analysis details if available
    if function_analyses:
        report["function_analyses"] = {}
        for func_name, func_paths in function_analyses.items():
            report["function_analyses"][func_name] = {
                "total_paths": len(func_paths),
                "satisfiable_paths": len(
                    [p for p in func_paths if getattr(p, "satisfiable", True)]
                ),
                "paths": [path.to_dict() for path in func_paths],
            }

    return report


def generate_fast_comprehensive_report(
    paths: List[Any],
    global_env_functions: Optional[Dict] = None,
    function_analyses: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Generate simplified report for performance mode"""
    satisfiable_paths = [p for p in paths if getattr(p, "satisfiable", True)]

    report = {
        "total_paths": len(paths),
        "satisfiable_paths": len(satisfiable_paths),
        "paths": [path.to_dict() for path in paths],
        "summary": {
            "functions_analyzed": len(global_env_functions)
            if global_env_functions
            else 0,
            "max_path_length": max(
                (len(getattr(p, "statements", [])) for p in paths), default=0
            ),
            "max_conditions": max(
                (len(getattr(p, "conditions", [])) for p in paths), default=0
            ),
            "performance_mode": True,
        },
    }

    # Add function analysis if available
    if function_analyses:
        report["function_analyses"] = {}
        for func_name, func_paths in function_analyses.items():
            report["function_analyses"][func_name] = {
                "total_paths": len(func_paths),
                "satisfiable_paths": len(
                    [p for p in func_paths if getattr(p, "satisfiable", True)]
                ),
                "paths": [path.to_dict() for path in func_paths],
            }

    return report


def renumber_paths_sequentially(paths: List[Any]) -> List[Any]:
    """Renumber paths sequentially starting from 1"""
    for i, path in enumerate(paths, 1):
        if hasattr(path, "path_id"):
            path.path_id = f"path_{i}"
    return paths
