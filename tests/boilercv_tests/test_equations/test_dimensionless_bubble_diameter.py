"""Equations."""

from inspect import Signature
from tomllib import loads

import pytest
from numpy import allclose
from sympy import lambdify

from boilercv_pipeline.correlations import dimensionless_bubble_diameter
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    EXPECTATIONS_TOML,
    KWDS,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    equations as symbolic,
)

lambdify  # noqa: B018

EXPECTATIONS = loads(EXPECTATIONS_TOML.read_text("utf-8"))


@pytest.mark.parametrize(("name", "expected"), EXPECTATIONS.items())
def test_python(name, expected):
    """Equations evaluate as expected."""
    equation = getattr(dimensionless_bubble_diameter, name)
    result = equation(**{
        kwd: value
        for kwd, value in KWDS.items()
        if kwd in Signature.from_callable(equation).parameters
    })
    assert allclose(result, expected)


@pytest.mark.skip()
@pytest.mark.parametrize("symbol_group_name", ["SYMS", "LONG_SYMS"])
def test_syms(symbol_group_name: str):
    """Declared symbolic variables assigned to correct symbols."""
    symbols = [group_sym.name for group_sym in getattr(symbolic, symbol_group_name)]
    variables = [name for name in symbols if getattr(symbolic, name)]
    assert symbols == variables


# TODO: Remove conditional in test parametrization once we're generating symbolics
# @pytest.mark.parametrize(
#     ("name", "expected"),
#     (
#         (name, expected)
#         for name, expected in EXPECTATIONS.items()
#         if name in "florschuetz_chao_1965"
#     ),
# )
# def test_sympy(name, expected):
#     """Symbolic equations evaluate as expected."""
#     mod = symbolic
#     correlation = lambdify(
#         expr=(expr := getattr(mod, name).rhs.subs(mod.SUBS)),
#         modules=numpy,
#         args=[s for s in expr.free_symbols if s.name in mod.SUBS.values()],  # type: ignore
#     )
#     result = correlation(**{
#         kwd: value
#         for kwd, value in KWDS.items()
#         if kwd in Signature.from_callable(correlation).parameters
#     })
#     assert allclose(result, expected)
