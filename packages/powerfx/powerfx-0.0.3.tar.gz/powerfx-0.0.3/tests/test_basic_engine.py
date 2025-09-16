import pytest

from powerfx import Engine  # type: ignore


def test_eval_raises_on_incorrect_inputs():
    engine = Engine()

    # expr is a number
    with pytest.raises(TypeError, match="expr must be a string"):
        engine.eval(123, symbols={"x": 1})

    # symbols is a number
    with pytest.raises(TypeError, match=r"symbols must be a dict\[str, Any\] or None"):
        engine.eval("1+1", symbols=123)


@pytest.mark.parametrize(
    "expr,expected",
    [
        ("1+1", 2),
        ("Sum(1,2,3)", 6),
        ("With({x:1}, x+2)", 3),
        ("If(true, 10, 20)", 10),
        ("Filter([1,2,3,4], Value > 2)", [3, 4]),
        ("First([1,2,3,5])", {"Value": 1}),
    ],
)
def test_basic_engine_eval(expr, expected):
    engine = Engine()
    result = engine.eval(expr)
    assert result == expected


@pytest.mark.parametrize(
    "expr,symbols,expected",
    [
        ("x + 1", {"x": 2}, 3),
        ("y * 2", {"y": 3}, 6),
        ("If(true, x, y)", {"x": 5, "y": 10}, 5),
        ("Filter(table, Value > threshold)", {"table": [1, 2, 3, 4], "threshold": 2}, [3, 4]),
    ],
)
def test_engine_eval_with_symbols(expr, symbols, expected):
    engine = Engine()
    result = engine.eval(expr, symbols=symbols)
    assert result == expected
