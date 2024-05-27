"""Bubble collapse correlation models."""

from string import whitespace
from typing import Generic

from pydantic import BaseModel, Field

from boilercv_pipeline.annotations import SK, Expr
from boilercv_pipeline.correlations.annotations import Equation, Kind, eqs, kinds
from boilercv_pipeline.mappings import regex_replace, replace
from boilercv_pipeline.mappings.models import Repl
from boilercv_pipeline.morphs import (
    ContextMorph,
    Defaults,
    LocalSymbols,
    Pipe,
    get_context,
    set_defaults,
)
from boilercv_pipeline.types import Context, K


class Forms(ContextMorph[Kind, str]):
    """Forms."""

    @classmethod
    def get_context(cls) -> Context:
        """Get context."""
        return get_context({cls: [Pipe(set_defaults, Defaults(keys=kinds, value=""))]})


class Equations(ContextMorph[Equation, Forms]):
    """Equations."""

    @classmethod
    def get_context(cls, local_symbols: LocalSymbols[SK]) -> Context:
        """Get morphs for {class}`Equations`."""
        return get_context(
            Forms.get_morphs()
            | {
                cls: [Pipe(set_defaults, Defaults(keys=eqs, factory=Forms))],
                Forms: [
                    *Forms.get_pipes(),
                    Pipe(fold_whitespace, Defaults(keys=kinds)),
                    Pipe(set_equation_forms, local_symbols),
                ],
            }
        )


def set_equation_forms(i: Forms, symbols: LocalSymbols[str]) -> Forms:
    """Set equation forms."""
    return i.pipe(
        replace,
        (
            Repl[Kind](src="sympy", dst="sympy", find=find, repl=repl)
            for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
        ),
    ).pipe(
        regex_replace,
        (
            Repl[Kind](src="sympy", dst="sympy", find=find, repl=repl)
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


class Params(ContextMorph[K, Forms], Generic[K]):
    """Parameters."""

    @classmethod
    def get_context(cls, default_keys: tuple[K, ...]) -> Context:
        """Get Pydantic context."""
        return get_context({
            cls: [Pipe(set_defaults, Defaults(keys=default_keys, value=""))],
            Forms: [
                *Forms.get_pipes(),
                Pipe(fold_whitespace, Defaults(keys=kinds)),
                set_latex_forms,
            ],
        })


def set_latex_forms(i: Forms) -> Forms:
    """Set forms for parameters."""
    if i["sympy"] and not i["latex"]:
        i["latex"] = i["sympy"]
    i = i.pipe(
        replace,
        repls=[
            Repl[Kind](src="latex", dst="sympy", find=k, repl=v)
            for k, v in {r"_\b0": "_bo", r"_\o": "_0", "\\": ""}.items()
        ],
    )
    return i


def fold_whitespace(i: dict[K, str], defaults: Defaults[K, str]) -> dict[K, str]:
    """Fold whitespace."""
    return replace(
        i,
        (
            Repl[K](src=key, dst=key, find=find, repl=" ")
            for find in whitespace
            for key in defaults.keys
        ),
    )


class Solutions(BaseModel):
    """Solutions for a symbol."""

    solutions: list[Expr] = Field(default_factory=list)
    """Solutions."""
    warnings: list[str] = Field(default_factory=list)
    """Warnings."""


class SymbolSolutions(ContextMorph[K, Solutions]):
    """Dimensionless bubble diameter solutions."""

    @classmethod
    def get_context(cls, solve_syms: tuple[K, ...]) -> Context:
        """Get Pydantic context."""
        return get_context({
            cls: [Pipe(set_defaults, Defaults(keys=solve_syms, factory=Solutions))]
        })


class EquationSolutions(ContextMorph[Equation, ContextMorph[K, Solutions]]):
    """Equation solutions."""

    @classmethod
    def get_context(cls, solve_syms: tuple[K, ...]) -> Context:
        """Get Pydantic context."""
        return get_context(
            SymbolSolutions.get_morphs(solve_syms=solve_syms)
            | {
                cls: [Pipe(set_defaults, Defaults(keys=eqs, factory=SymbolSolutions))],
                ContextMorph[K, Solutions]: [
                    Pipe(set_defaults, Defaults(keys=solve_syms, factory=Solutions))
                ],
            }
        )
