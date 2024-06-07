"""Equations."""

from inspect import Signature
from tomllib import loads

import pytest
from numpy import allclose
from sympy import lambdify

from boilercv.correlations import SYMBOLS, dimensionless_bubble_diameter
from boilercv.correlations import dimensionless_bubble_diameter as symbolic
from boilercv.correlations.dimensionless_bubble_diameter import (
    EXPECTATIONS_TOML,
    SYMBOL_EXPECTATIONS,
    get_correlations,
)

lambdify  # noqa: B018

EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))
CORRELATIONS = get_correlations()


@pytest.mark.parametrize(("name", "expected"), EXPECTATIONS.items())
def test_python(name, expected):
    """Equations evaluate as expected."""
    equation = getattr(dimensionless_bubble_diameter, name)
    result = equation(**{
        SYMBOLS[kwd]: value
        for kwd, value in SYMBOL_EXPECTATIONS.items()
        if SYMBOLS[kwd] in Signature.from_callable(equation).parameters
    })
    assert allclose(result, expected)


@pytest.mark.skip()
@pytest.mark.parametrize("symbol_group_name", ["SYMS", "LONG_SYMS"])
def test_syms(symbol_group_name: str):
    """Declared symbolic variables assigned to correct symbols."""
    symbols = [group_sym.name for group_sym in getattr(symbolic, symbol_group_name)]
    variables = [name for name in symbols if getattr(symbolic, name)]
    assert symbols == variables


@pytest.mark.parametrize(
    ("name", "corr", "expected"),
    (
        (name, CORRELATIONS[name], expected)  # pyright: ignore[reportArgumentType]
        for name, expected in EXPECTATIONS.items()
        if name in EXPECTATIONS
    ),
)
def test_sympy(name, corr, expected):
    """Symbolic equations evaluate as expected."""
    result = corr(**{
        kwd: value
        for kwd, value in SYMBOL_EXPECTATIONS.items()
        if kwd in Signature.from_callable(corr).parameters
    })
    assert allclose(result, expected, rtol=1.0e-4)
