"""Runtime type annotations for bubble collapse correlations.."""

from collections import UserDict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from re import Pattern
from typing import Any, Literal, TypeAlias, get_args

from sympy import Symbol, symbols

from boilercv.morphs.types.runtime import ContextValue

Kind: TypeAlias = Literal["latex", "sympy"]
"""Kind."""
Equation: TypeAlias = Literal[
    "florschuetz_chao_1965", "isenberg_sideman_1970", "akiyama_1973", "yuan_et_al_2009"
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


@dataclass
class KeysPattern(ContextValue):
    """Keys pattern."""

    pattern: Pattern[str]
    group: str
    apply_to_match: Callable[[str], Any] = str
    message: str = "Match not found when sorting."
