"""Types for dimensionless collapsing bubble diameter correlations."""

from typing import Literal, TypeAlias, get_args

from pydantic import BeforeValidator
from sympy import Basic, sympify

from boilercv.morphs import Morph
from boilercv_pipeline.types import Expr

Sym: TypeAlias = Literal["Fo_0", "Ja", "Re_b0", "Pr", "beta", "pi"]
"""Symbol."""
syms: tuple[Sym, ...] = get_args(Sym)
"""Symbols."""
solve_syms: tuple[Sym, ...] = ("beta",)
"""Symbols to solve for."""
Param: TypeAlias = Literal[
    "bubble_fourier",
    "bubble_jakob",
    "bubble_initial_reynolds",
    "liquid_prandtl",
    "dimensionless_bubble_diameter",
    "pi",
]
"""Parameter."""
params: tuple[Param, ...] = get_args(Param)
"""Parameters."""
Locals: TypeAlias = Morph[Sym, Expr]
"""Locals."""


def SolnValidator(loc: Locals) -> BeforeValidator:  # noqa: N802; Can't inherit from frozen
    """Validate solution."""

    def validate(v: Basic | str) -> Basic:
        return (
            sympify(v, locals=loc.model_dump(), evaluate=False)
            if isinstance(v, str)
            else v
        )

    return BeforeValidator(validate)
