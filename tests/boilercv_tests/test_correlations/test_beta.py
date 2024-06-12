"""Equations."""

from inspect import Signature
from tomllib import loads

import pytest
from numpy import allclose, bool_

from boilercv.correlations import SYMBOLS, beta
from boilercv.correlations.beta import (
    EXPECTATIONS_TOML,
    SYMBOL_EXPECTATIONS,
    get_correlations,
)

EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))
CORRELATIONS = get_correlations()
exprs = {name: corr.expr for name, corr in CORRELATIONS.items()}
ranges = {name: corr.range for name, corr in CORRELATIONS.items()}


@pytest.mark.parametrize(("name", "expected"), EXPECTATIONS.items())
def test_python(name, expected):
    """Equations evaluate as expected."""
    equation = getattr(beta, name)
    result = equation(**{
        SYMBOLS[kwd]: value
        for kwd, value in SYMBOL_EXPECTATIONS.items()
        if SYMBOLS[kwd] in Signature.from_callable(equation).parameters
    })
    assert allclose(result, expected)


@pytest.mark.parametrize(
    ("corr", "expected"),
    ((exprs[name], expected) for name, expected in EXPECTATIONS.items()),
    ids=EXPECTATIONS,
)
def test_correlations(corr, expected):
    """Symbolic equations evaluate as expected."""
    result = corr(**{
        kwd: value
        for kwd, value in SYMBOL_EXPECTATIONS.items()
        if kwd in Signature.from_callable(corr).parameters
    })
    assert allclose(result, expected, rtol=1.0e-4)


@pytest.mark.parametrize(
    ("range_"), (ranges[name] for name in EXPECTATIONS), ids=EXPECTATIONS
)
def test_correlation_ranges(range_):
    """Symbolic ranges evaluate as expected."""
    if not range_:
        return
    assert isinstance(
        range_(**{
            kwd: value
            for kwd, value in {
                "Nu_c": 1.0,
                "Ja": 1.0,
                "Re_b": 1.0,
                "Pe": 1.0,
                "Pr": 1.0,
                "alpha": 1.0,
            }.items()
            if kwd in Signature.from_callable(range_).parameters
        }),
        bool_,
    )
