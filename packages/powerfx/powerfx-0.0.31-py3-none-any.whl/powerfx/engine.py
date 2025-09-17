from __future__ import annotations

from typing import Any

from powerfx._loader import load
from powerfx._utility import _create_cancellation_token, _formulavalue_to_python, _python_to_formulavalue

load()
# Import after load so the assemblies are visible.
from Microsoft.PowerFx import (  # type: ignore  # noqa: E402
    CheckResultExtensions,
    ReadOnlySymbolTable,
    ReadOnlySymbolValues,
    RuntimeConfig,
    SymbolTable,
)
from Microsoft.PowerFx import RecalcEngine as _RecalcEngine  # type: ignore  # noqa: E402
from Microsoft.PowerFx.Types import RecordValue  # type: ignore  # noqa: E402


class Engine:
    """
    Minimal wrapper around Microsoft.PowerFx RecalcEngine.
    - eval(expr: str) -> Python value
    - set(name: str, value: any) to bind variables
    """

    def __init__(self) -> None:
        # Load CLR + PowerFx assemblies first, using dll_dir or env var.

        self._engine = _RecalcEngine()

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

        sym_vals: ReadOnlySymbolTable = None
        if symbols:
            parameter_record_value = _python_to_formulavalue(symbols)  # validate
            if not isinstance(parameter_record_value, RecordValue):
                raise TypeError("symbols must convert to a RecordValue")
            sym_vals = ReadOnlySymbolValues.NewFromRecord(parameter_record_value)

        cancellation_token = _create_cancellation_token(timeout)
        symbol_table: ReadOnlySymbolTable | None = sym_vals.SymbolTable if symbols else SymbolTable()
        check = _compile(self, expr, symbol_table)  # noqa: F841

        runtime_config = RuntimeConfig(sym_vals)
        result = CheckResultExtensions.GetEvaluator(check).EvalAsync(cancellation_token, runtime_config).Result
        # returns FormulaValue
        # result = self._engine.EvalAsync(expr, cancellation_token, sym_vals).Result  # returns FormulaValue

        pyResult = _formulavalue_to_python(result)
        return pyResult


def _compile(self, expr: str, symbols: Any | None = None) -> Any:
    """
    Check/parse an expression once and return a reusable evaluator/runner.
    Raises ValueError with detailed messages if check fails.
    """
    if not isinstance(expr, str):
        raise TypeError("expr must be a string")
    if symbols is not None and not isinstance(symbols, ReadOnlySymbolTable):
        raise TypeError("symbols must be a ReadOnlySymbolTable or None found " + str(type(symbols)))

    check = self._engine.Check(expr, None, symbols)  # returns CheckResult
    if not check.IsSuccess:
        # Build a friendly error message (you can surface spans/severity too)
        msgs = []
        for err in check.Errors:
            # err.Message typically has the human-readable reason
            # err.Span.Min/Max give positions; Severity is usually Error/Warning
            msgs.append("Error " + str(err.Span.Min) + " - " + str(err.Span.Lim) + " : " + str(err.Message))
        raise ValueError("Power Fx failed compilation: " + "; ".join(msgs))

    return check
