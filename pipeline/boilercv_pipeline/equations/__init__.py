"""Equation processing."""

from typing import cast, get_args

from boilercv.correlations import dimensionless_bubble_diameter, nusselt
from boilercv.correlations.dimensionless_bubble_diameter.types import SolveSym

_expectations = {
    "beta": dimensionless_bubble_diameter.SYMBOL_EXPECTATIONS | {"Fo_0": 0.0},
    "nusselt": nusselt.SYMBOL_EXPECTATIONS | {"Fo_0": 0.0},
}

EQUATIONS = {
    "beta": dimensionless_bubble_diameter.EQUATIONS_TOML,
    "nusselt": nusselt.EQUATIONS_TOML,
}
SOLUTIONS = {
    "beta": dimensionless_bubble_diameter.SOLUTIONS_TOML,
    "nusselt": nusselt.SOLUTIONS_TOML,
}
EXPECTATIONS = {
    "beta": dimensionless_bubble_diameter.EXPECTATIONS_TOML,
    "nusselt": nusselt.EXPECTATIONS_TOML,
}
SUBSTITUTIONS = {
    corr: cast(tuple[tuple[str, float], ...], tuple(expectations.items()))
    for corr, expectations in _expectations.items()
}
SYMS = {
    corr: tuple(expectations.keys()) for corr, expectations in _expectations.items()
}
SOLVE_SYMS = {"beta": get_args(SolveSym), "nusselt": get_args(SolveSym)}
