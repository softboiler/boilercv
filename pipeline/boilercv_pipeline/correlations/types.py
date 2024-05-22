"""Type for subcooled bubble collapse correlations."""

from typing import Literal, TypeAlias, get_args

from boilercv_pipeline.types import Repl

Kind: TypeAlias = Literal["latex", "sympy", "python"]
"""Kind."""
kinds: tuple[Kind, ...] = get_args(Kind)
"""Equation kinds."""
FormsRepl: TypeAlias = Repl[Kind]
"""Forms replacements."""
Eq: TypeAlias = Literal[
    "florschuetz_chao_1965", "isenberg_sideman_1970", "akiyama_1973", "yuan_et_al_2009"
]
"""Equation."""
