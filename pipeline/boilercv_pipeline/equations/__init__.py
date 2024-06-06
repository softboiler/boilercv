"""Equation processing."""

from typing import cast, get_args

from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    EQUATIONS_TOML,
    EXPECTATIONS_TOML,
    SOLUTIONS_TOML,
    SYMBOL_EXPECTATIONS,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import SolveSym

default_equations = EQUATIONS_TOML
default_solutions = SOLUTIONS_TOML
default_expectations = EXPECTATIONS_TOML
_overridden_symbol_expectations = SYMBOL_EXPECTATIONS | {"Fo_0": 0.0}
default_substitutions = cast(
    tuple[tuple[str, float], ...], tuple((_overridden_symbol_expectations).items())
)
default_syms = tuple(_overridden_symbol_expectations.keys())
default_solve_syms = get_args(SolveSym)
