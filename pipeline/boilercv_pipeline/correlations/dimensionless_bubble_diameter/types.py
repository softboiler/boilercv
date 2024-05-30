"""Types for dimensionless collapsing bubble diameter correlations."""

from typing import Literal, TypeAlias, get_args

Sym: TypeAlias = Literal["Fo_0", "Ja", "Re_b0", "Pr", "beta", "pi"]
"""Symbol."""
syms: tuple[Sym, ...] = get_args(Sym)
"""Symbols."""
SolveSym: TypeAlias = Literal["beta"]
"""Solve symbol."""
solve_syms: tuple[SolveSym, ...] = get_args(SolveSym)
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
