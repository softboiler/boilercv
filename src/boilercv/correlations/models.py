"""Bubble collapse correlation models."""

from collections.abc import Iterable
from functools import partial
from typing import Generic, get_args

from numpy import nan
from pydantic import Field

from boilercv.correlations.pipes import (
    LocalSymbols,
    compose_sympify_context,
    fold_whitespace,
    set_equation_forms,
    set_latex_forms,
    sort_by_year,
)
from boilercv.correlations.types import EQ, Eq, Equation, Expectation, Expr, K, Kind, S
from boilercv.morphs.contexts import (
    Context,
    ContextBaseModel,
    ContextMorph,
    Defaults,
    Pipe,
    compose_contexts,
    make_pipelines,
)


class Expectations(ContextMorph[K, Expectation], Generic[K]):
    """Expectations."""

    @classmethod
    def get_context(cls) -> Context:
        """Get Pydantic context."""
        Keys, *_ = cls.__pydantic_generic_metadata__["args"]  # noqa: N806
        return cls.compose_defaults(keys=get_args(Keys), value=nan)


class Forms(ContextMorph[Kind, str]):
    """Forms."""

    @classmethod
    def get_context(cls, symbols: Iterable[str]) -> Context:
        """Get context."""
        return compose_contexts(
            cls.compose_defaults(value=""),
            make_pipelines(
                cls,
                before=[
                    Pipe(fold_whitespace, Defaults(keys=get_args(Kind))),
                    Pipe(set_equation_forms, LocalSymbols.from_iterable(symbols)),
                ],
            ),
        )


class Params(ContextMorph[K, Forms], Generic[K]):
    """Parameters."""

    @classmethod
    def get_context(cls, symbols: Iterable[str]) -> Context:
        """Get Pydantic context."""
        return compose_contexts(
            cls.compose_defaults(value_context=Forms.get_context(symbols=symbols)),
            make_pipelines(Forms, after=[set_latex_forms]),
        )


def prep_equation_forms(i: dict[Kind, str], context: Context) -> dict[Kind, str]:
    """Prepare equation forms."""
    return (Forms.context_model_validate(i, context=context)).model_dump()


class EquationForms(ContextBaseModel, Generic[EQ]):
    """Equation forms."""

    latex: str
    """LaTeX form."""
    sympy: EQ
    """Symbolic form."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str] | None = None, forms_context: Context | None = None
    ) -> Context:
        """Get context."""
        symbols = symbols or ()
        forms_context = forms_context or Forms.get_context(symbols=symbols)
        return compose_contexts(
            make_pipelines(
                cls, before=partial(prep_equation_forms, context=forms_context)
            ),
            forms_context,
        )


class Equations(ContextMorph[Equation, EquationForms[EQ]], Generic[EQ]):
    """Equations."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str] | None = None, forms_context: Context | None = None
    ) -> Context:
        """Get context."""
        symbols = symbols or ()
        sympify_context = compose_sympify_context(symbols)  # If `EQ` is `Eq`
        Eq_, *_ = cls.__pydantic_generic_metadata__["args"]  # noqa: N806
        k, _ = cls.morph_get_inner_types()
        return compose_contexts(
            cls.compose_defaults(
                keys=get_args(k),
                value_context=EquationForms[Eq_].get_context(
                    symbols=symbols,
                    forms_context=compose_contexts(
                        forms_context or Forms.get_context(symbols=symbols),
                        sympify_context,
                    ),
                ),
            ),
            make_pipelines(cls, before=sort_by_year),
            sympify_context,
        )


class Solutions(ContextBaseModel):
    """Solutions for a symbol."""

    solutions: list[Expr] = Field(default_factory=list)
    """Solutions."""
    warnings: list[str] = Field(default_factory=list)
    """Warnings."""

    @classmethod
    def get_context(cls, symbols: Iterable[str]) -> Context:
        """Get Pydantic context."""
        return compose_sympify_context(symbols)  # for `Expr`


class SymbolSolutions(ContextMorph[S, Solutions], Generic[S]):
    """Solutions for given symbols."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str], solve_syms: tuple[str, ...] | None = None
    ) -> Context:
        """Get Pydantic context."""
        SolveSyms, *_ = cls.__pydantic_generic_metadata__["args"]  # noqa: N806
        return cls.compose_defaults(
            keys=solve_syms or get_args(SolveSyms),
            value_context=Solutions.get_context(symbols=symbols),
        )


class EquationSolutions(ContextMorph[Equation, SymbolSolutions[S]], Generic[S]):
    """Equation solutions."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str], solve_syms: tuple[str, ...] | None = None
    ) -> Context:
        """Get Pydantic context."""
        SolveSyms, *_ = cls.__pydantic_generic_metadata__["args"]  # noqa: N806
        return compose_contexts(
            cls.compose_defaults(
                value_context=SymbolSolutions[SolveSyms].get_context(
                    symbols=symbols, solve_syms=solve_syms
                )
            ),
            make_pipelines(cls, before=sort_by_year),
        )


class SolvedEquations(ContextBaseModel, Generic[S]):
    """Solved equations."""

    equations: Equations[Eq]
    """Equations."""
    solutions: EquationSolutions[S]
    """Solutions."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str], solve_syms: tuple[str, ...]
    ) -> Context:
        """Get Pydantic context."""
        SolveSyms, *_ = cls.__pydantic_generic_metadata__["args"]  # noqa: N806
        return compose_contexts(
            Equations[Eq].get_context(
                symbols=symbols,
                forms_context=compose_contexts(Forms.get_context(symbols)),
            ),
            EquationSolutions[SolveSyms].get_context(
                symbols=symbols, solve_syms=solve_syms
            ),
        )
