"""Types."""

from typing import Annotated, Literal, TypeAlias, TypeVar

from boilercv_pipeline.types import Eq, LiteralKeys, StrSerializer, TypeValidator

K = TypeVar("K")
V = TypeVar("V")

S = TypeVar(
    "S", bound=Annotated[LiteralKeys, TypeValidator(str), StrSerializer("json")] | str
)
"""Keys representing symbols."""

EQ = TypeVar("EQ", bound=Eq | str)
"""SymPy symbolic equation or string type."""

Kind: TypeAlias = Literal["latex", "sympy"]
"""Kind."""
Equation: TypeAlias = Literal[
    "florschuetz_chao_1965", "isenberg_sideman_1970", "akiyama_1973", "yuan_et_al_2009"
]
"""Equation."""
