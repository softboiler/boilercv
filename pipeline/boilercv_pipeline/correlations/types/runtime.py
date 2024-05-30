"""Runtime type annotations for bubble collapse correlations.."""

from typing import Literal, TypeAlias, get_args

Kind: TypeAlias = Literal["latex", "sympy"]
"""Kind."""
Equation: TypeAlias = Literal[
    "akiyama_1973", "florschuetz_chao_1965", "isenberg_sideman_1970", "yuan_et_al_2009"
]
"""Equation."""
kinds: tuple[Kind, ...] = get_args(Kind)
"""Equation kinds."""
eqs: tuple[Equation, ...] = get_args(Equation)
"""Equations."""
