from __future__ import annotations

from typing import Any

from powerfx._loader import load
from powerfx._utility import _create_cancellation_token, _formulavalue_to_python, _python_to_formulavalue


class Engine:
    """
    Minimal wrapper around Microsoft.PowerFx RecalcEngine.
    - eval(expr: str) -> Python value
    - set(name: str, value: any) to bind variables
    """

    def __init__(self) -> None:
        # Load CLR + PowerFx assemblies first, using dll_dir or env var.
        load()
        print("Power Fx assemblies loaded successfully.")
        # Import after load so the assemblies are visible.
        from Microsoft.PowerFx import RecalcEngine as _RecalcEngine  # type: ignore

        self._engine = _RecalcEngine()

    # def eval(self, expr: str) -> Any:
    #     """
    #     Evaluate a Power Fx expression and return a Python-native object where possible.
    #     """
    #     if not isinstance(expr, str):
    #         raise TypeError("expr must be a string")
    #     result = self._engine.Eval(expr)  # returns FormulaValue
    #     pyResult = _formulavalue_to_python(result)
    #     return pyResult

    def eval(self, expr: str, symbols: dict[str, Any] | None = None, timeout: float | None = None) -> Any:
        """
            Evaluate a Power Fx expression and return a Python-native object where possible.
        Optionally pass a dictionary of symbols to bind before evaluation.

        Args:
            expr (str): The Power Fx expression to evaluate.
            symbols (dict[str, Any] | None): Optional dictionary of symbols.
            timeout (float | None): Timeout in seconds. If None, no timeout is applied.
        """
        if not isinstance(expr, str):
            raise TypeError("expr must be a string")
        if symbols is not None and not isinstance(symbols, dict):
            raise TypeError("symbols must be a dict[str, Any] or None")

        sym_vals = None
        if symbols:
            sym_vals = _python_to_formulavalue(symbols)  # validate

        cancellation_token = _create_cancellation_token(timeout)
        result = self._engine.EvalAsync(expr, cancellation_token, sym_vals).Result  # returns FormulaValue

        pyResult = _formulavalue_to_python(result)
        return pyResult
