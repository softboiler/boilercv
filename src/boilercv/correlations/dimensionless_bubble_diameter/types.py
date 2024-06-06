"""Types for dimensionless collapsing bubble diameter correlations."""

from typing import Literal, TypeAlias

Sym: TypeAlias = Literal["Fo_0", "Ja", "Re_b0", "Pr", "beta", "pi"]
"""Symbol."""
SolveSym: TypeAlias = Literal["beta"]
"""Solve symbol."""
Param: TypeAlias = Literal[
    "bubble_fourier",
    "bubble_jakob",
    "bubble_initial_reynolds",
    "liquid_prandtl",
    "dimensionless_bubble_diameter",
    "pi",
]
"""Parameter."""
