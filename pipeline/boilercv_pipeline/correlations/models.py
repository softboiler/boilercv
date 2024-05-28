"""Bubble collapse correlation models."""

from collections.abc import Iterable
from string import whitespace
from typing import Generic

from pydantic import BaseModel, Field

from boilercv.mappings import regex_replace, replace
from boilercv.mappings.models import Repl
from boilercv.morphs.contexts import (
    Context,
    ContextMorph,
    Defaults,
    LocalSymbols,
    Morphs,
    Pipe,
    compose_context,
    set_defaults,
)
from boilercv.morphs.types import K
from boilercv_pipeline.correlations.annotations import Equation, Kind, eqs, kinds
from boilercv_pipeline.types.runtime import Expr, SympifyParams


class Forms(ContextMorph[Kind, str]):
    """Forms."""

    @classmethod
    def get_context(cls) -> Context:
        """Get context."""
        return compose_context(
            Morphs({cls: [Pipe(set_defaults, Defaults(keys=kinds, value=""))]})
        )


class Equations(ContextMorph[Equation, Forms]):
    """Equations."""

    @classmethod
    def get_context(cls, symbols: Iterable[str]) -> Context:
        """Get context."""
        return Forms.get_context() | compose_context(
            Morphs({
                cls: [Pipe(set_defaults, Defaults(keys=eqs, factory=Forms))],
                Forms: [
                    Pipe(fold_whitespace, Defaults(keys=kinds)),
                    Pipe(set_equation_forms, LocalSymbols.from_iterable(symbols)),
                ],
            })
        )


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


def set_equation_forms(i: Forms, symbols: LocalSymbols) -> Forms:
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
        return Forms.get_context() | compose_context(
            Morphs({
                cls: [Pipe(set_defaults, Defaults(keys=default_keys, value=""))],
                Forms: [Pipe(fold_whitespace, Defaults(keys=kinds)), set_latex_forms],
            })
        )


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


class Solutions(BaseModel):
    """Solutions for a symbol."""

    solutions: list[Expr] = Field(default_factory=list)
    """Solutions."""
    warnings: list[str] = Field(default_factory=list)
    """Warnings."""

    @classmethod
    def get_context(cls, symbols: Iterable[str]) -> Context:
        """Get Pydantic context."""
        return compose_context(
            # ? For `Expr`
            SympifyParams(
                locals=dict(LocalSymbols.from_iterable(symbols)), evaluate=False
            )
        )


class SymbolSolutions(ContextMorph[K, Solutions], Generic[K]):
    """Solutions for given symbols."""

    @classmethod
    def get_context(cls, symbols: Iterable[str], solve_syms: tuple[K, ...]) -> Context:
        """Get Pydantic context."""
        return Solutions.get_context(symbols=symbols) | compose_context(
            Morphs({
                cls: [Pipe(set_defaults, Defaults(keys=solve_syms, factory=Solutions))]
            })
        )


class EquationSolutions(ContextMorph[Equation, SymbolSolutions[K]], Generic[K]):
    """Equation solutions."""

    @classmethod
    def get_context(cls, symbols: Iterable[str], solve_syms: tuple[K, ...]) -> Context:
        """Get Pydantic context."""
        return (
            SymbolSolutions.get_context(symbols=symbols, solve_syms=solve_syms)
        ) | compose_context(
            Morphs({
                cls: [Pipe(set_defaults, Defaults(keys=eqs, factory=SymbolSolutions))],
                SymbolSolutions: [
                    Pipe(set_defaults, Defaults(keys=solve_syms, factory=Solutions))
                ],
            })
        )
