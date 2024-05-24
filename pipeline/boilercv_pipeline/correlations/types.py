"""Type for subcooled bubble collapse correlations."""

from __future__ import annotations

from string import whitespace
from typing import (
    Any,
    ClassVar,
    Generic,
    Literal,
    Protocol,
    TypeAlias,
    TypeVar,
    get_args,
)

from pydantic import ValidationInfo
from typing_extensions import TypedDict

from boilercv.morphs import Morph
from boilercv_pipeline.morphs import DefaultMorph, Solutions, regex_replace, replace
from boilercv_pipeline.types import LocalSymbols, Repl

Kind: TypeAlias = Literal["latex", "sympy", "python"]
"""Kind."""
kinds: tuple[Kind, ...] = get_args(Kind)
"""Equation kinds."""
FormsRepl: TypeAlias = Repl[Kind]
"""Forms replacements."""
Equation: TypeAlias = Literal[
    "florschuetz_chao_1965", "isenberg_sideman_1970", "akiyama_1973", "yuan_et_al_2009"
]
"""Equation."""
eqs: tuple[Equation, ...] = get_args(Equation)
"""Equations."""


class FormsContext(TypedDict):
    """Context for expression validation."""

    locals: LocalSymbols
    """Local symbols."""


class FormsValidationInfo(ValidationInfo, Protocol):
    """Argument passed to validation functions."""

    @property
    def context(self) -> FormsContext | None:
        """Current validation context."""


def set_equation_forms(i: Forms, context: FormsContext | None) -> Forms:
    """Set equation forms."""
    symbols = ctx["locals"] if (ctx := context) else {}
    return (
        i.pipe(
            replace,
            (
                FormsRepl(src=kind, dst=kind, find=find, repl=" ")
                for find in whitespace
                for kind in kinds
            ),
        )
        .pipe(
            replace,
            (
                FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
                for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
            ),
        )
        .pipe(
            regex_replace,
            (
                FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
                for sym in symbols
                for find, repl in {
                    # ? Symbol split by `(` after first character.
                    rf"{sym[0]}\*\({sym[1:]}([^)]+)\)": rf"{sym}\g<1>",
                    # ? Symbol split by a `*` after first character.
                    rf"{sym[0]}\*{sym[1:]}": rf"{sym}",
                    # ? Symbol missing `*` resulting in failed attempt to call it
                    rf"{sym}\(": rf"{sym}*(",
                }.items()
            ),
        )
    )


class Forms(DefaultMorph[Kind, str]):
    """Forms."""

    default_keys: ClassVar = kinds
    default: ClassVar = ""

    def model_post_init(self, context: FormsContext | None):
        """Set equation forms."""
        super().model_post_init(context)
        with self.thaw_self(validate=True):
            self.root = self.pipe(set_equation_forms, context=context).root


DefaultMorph.register(Forms)


class Equations(DefaultMorph[Equation, Forms]):
    """Equation forms."""

    default_keys: ClassVar[tuple[Equation, ...]] = eqs
    default_factory: ClassVar = Forms


DefaultMorph.register(Equations)


SymbolSolutions_T = TypeVar("SymbolSolutions_T", bound=Morph[Any, Solutions])
"""Symbol solutions type."""


class EquationSolutions(
    DefaultMorph[Equation, SymbolSolutions_T], Generic[SymbolSolutions_T]
):
    """Equation solutions."""

    default_keys: ClassVar[tuple[Equation, ...]] = eqs


DefaultMorph.register(EquationSolutions)
