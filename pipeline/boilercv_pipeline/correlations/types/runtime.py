"""Runtime type annotations for bubble collapse correlations.."""

from collections import UserDict
from collections.abc import Iterable
from typing import Literal, TypeAlias, get_args

from sympy import Symbol, symbols

from boilercv.morphs.types.runtime import ContextValue

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


class LocalSymbols(UserDict[str, Symbol], ContextValue):
    """Local symbols."""

    @classmethod
    def from_iterable(cls, syms: Iterable[str]):
        """Create from an iterable of symbols."""
        return cls(
            zip(
                syms,
                symbols(syms, nonnegative=True, real=True, finite=True),
                strict=True,
            )
        )
