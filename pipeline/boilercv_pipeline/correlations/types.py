"""Type for subcooled bubble collapse correlations."""

from __future__ import annotations

from string import whitespace
from typing import Literal, TypeAlias, get_args

from boilercv_pipeline.morphs import CtxMorph, regex_replace, replace, set_defaults
from boilercv_pipeline.types import SK, Defaults, LocalSymbols, Morphs, Pipe, Repl

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


class Forms(CtxMorph[Kind, str]):
    """Forms."""

    @classmethod
    def get_morphs(cls, local_symbols: LocalSymbols[SK]) -> Morphs:
        """Get morphs."""
        return Morphs({
            Forms: [
                Pipe(set_defaults, Defaults(default_keys=kinds, default="")),
                Pipe(set_equation_forms, local_symbols),
            ]
        })


CtxMorph.register(Forms)


def set_equation_forms(i: Forms, symbols: LocalSymbols[str]) -> Forms:
    """Set equation forms."""
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


class Equations(CtxMorph[Equation, Forms]):
    """Equations."""

    @classmethod
    def get_morphs(cls, local_symbols: LocalSymbols[SK]) -> Morphs:
        """Get morphs for {class}`Equations`."""
        return Morphs(
            {
                Equations: [
                    Pipe(
                        set_defaults, Defaults(default_keys=eqs, default_factory=Forms)
                    )
                ]
            }
            | Forms.get_morphs(local_symbols)
        )
