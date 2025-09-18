"""
PolyPrime Runtime - Simple execution environment
"""

from typing import Any, Dict

class Runtime:
    """Runtime for PolyPrime programs"""

    def __init__(self):
        self.globals: Dict[str, Any] = {}

    def execute_source(self, source: str) -> Any:
        """Execute PolyPrime source code"""
        from .compiler import Compiler

        compiler = Compiler()
        python_code = compiler.compile(source, "python")

        # Execute in safe environment
        local_vars = {}
        try:
            exec(python_code, {"__builtins__": {}}, local_vars)
            return local_vars
        except Exception as e:
            raise RuntimeError(f"Execution error: {e}")

    def execute_python(self, code: str) -> Any:
        """Execute Python code"""
        local_vars = {}
        exec(code, {"__builtins__": {}}, local_vars)
        return local_vars