"""Bubble collapse correlation models."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import partial
from typing import Any, Generic, get_args

import sympy
from numpy import nan
from pydantic import BaseModel, Field
from sympy.logic.boolalg import Boolean

from boilercv.correlations.pipes import (
    compose_sympify_context,
    fold_whitespace,
    set_latex_forms,
    sort_by_year,
)
from boilercv.correlations.types import (
    EQ,
    AnyEquation,
    Eq,
    Equation,
    Expectation,
    Expr,
    K,
    Kind,
    S,
)
from boilercv.morphs import Morph
from boilercv.pipelines import (
    Defaults,
    Pipeline,
    PipelineBase,
    compose_contexts,
    make_pipelines,
)
from boilercv.pipelines.contexts import PipelineCtx, get_pipeline_context
from boilercv.pipelines.pipes import Pipe


class EquationMetadata(BaseModel):
    """Meta."""

    name: str = ""
    """Name."""
    citekey: str = ""
    """Citekey."""


class Metadata(Pipeline[AnyEquation, EquationMetadata]):
    """Equations."""

    @classmethod
    def get_context(cls) -> PipelineCtx:
        """Get context."""
        return compose_contexts(
            cls.compose_defaults(), make_pipelines(cls, before=sort_by_year)
        )


class Expectations(Pipeline[K, Expectation], Generic[K]):
    """Expectations."""

    @classmethod
    def get_context(cls) -> PipelineCtx:
        """Get Pydantic context."""
        return cls.compose_defaults(value=nan)


class Forms(Pipeline[Kind, str]):
    """Forms."""

    @classmethod
    def get_context(cls) -> PipelineCtx:
        """Get context."""
        return compose_contexts(cls.compose_defaults(value=""))


class Params(Pipeline[K, Forms], Generic[K]):
    """Parameters."""

    @classmethod
    def get_context(cls) -> PipelineCtx:
        """Get Pydantic context."""
        return compose_contexts(
            cls.compose_defaults(value_context=Forms.get_context()),
            make_pipelines(Forms, after=[set_latex_forms]),
        )


def prep_equation_forms(
    i: dict[Kind, str], context: PipelineCtx | None = None
) -> Morph[Kind, str]:
    """Prepare equation forms."""
    return Forms.model_validate(
        obj=i,
        context=get_pipeline_context(
            context
            or make_pipelines(
                Forms,
                before=[
                    Forms.get_context().pipelines[Forms].before[0],
                    Pipe(fold_whitespace, Defaults(keys=get_args(Kind))),
                ],
            )
        ),
    )


class EquationForms(PipelineBase, Generic[EQ]):
    """Equation forms."""

    latex: str
    """LaTeX form."""
    sympy: EQ
    """Symbolic form."""

    @classmethod
    def get_context(
        cls,
        symbols: Iterable[str] | None = None,
        forms_context: PipelineCtx | None = None,
    ) -> PipelineCtx:
        """Get context."""
        symbols = symbols or ()
        return compose_contexts(
            make_pipelines(
                cls, before=partial(prep_equation_forms, context=forms_context)
            ),
            compose_sympify_context(symbols),  # If `EQ` is `Eq`
        )


class Equations(Pipeline[Equation, EquationForms[EQ]], Generic[EQ]):
    """Equations."""

    @classmethod
    def get_context(
        cls,
        symbols: Iterable[str] | None = None,
        forms_context: PipelineCtx | None = None,
    ) -> PipelineCtx:
        """Get context."""
        symbols = symbols or ()
        Eq_, *_ = cls.__pydantic_generic_metadata__["args"]  # noqa: N806
        return compose_contexts(
            cls.compose_defaults(
                value_context=EquationForms[Eq_].get_context(
                    symbols=symbols, forms_context=forms_context
                )
            ),
            make_pipelines(cls, before=sort_by_year),
        )


class Solutions(PipelineBase):
    """Solutions for a symbol."""

    solutions: list[Expr] = Field(default_factory=list)
    """Solutions."""
    warnings: list[str] = Field(default_factory=list)
    """Warnings."""

    @classmethod
    def get_context(cls, symbols: Iterable[str]) -> PipelineCtx:
        """Get Pydantic context."""
        return compose_sympify_context(symbols)  # for `Expr`


class SymbolSolutions(Pipeline[S, Solutions], Generic[S]):
    """Solutions for given symbols."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str], solve_syms: tuple[S, ...] | None = None
    ) -> PipelineCtx:
        """Get Pydantic context."""
        return cls.compose_defaults(
            keys=solve_syms, value_context=Solutions.get_context(symbols=symbols)
        )


class EquationSolutions(Pipeline[Equation, SymbolSolutions[S]], Generic[S]):
    """Equation solutions."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str], solve_syms: tuple[str, ...] | None = None
    ) -> PipelineCtx:
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


class SolvedEquations(PipelineBase, Generic[S]):
    """Solved equations."""

    equations: Equations[Eq]
    """Equations."""
    solutions: EquationSolutions[S]
    """Solutions."""

    @classmethod
    def get_context(
        cls, symbols: Iterable[str], solve_syms: tuple[str, ...]
    ) -> PipelineCtx:
        """Get Pydantic context."""
        SolveSyms, *_ = cls.__pydantic_generic_metadata__["args"]  # noqa: N806
        return compose_contexts(
            Equations[Eq].get_context(symbols=symbols),
            EquationSolutions[SolveSyms].get_context(
                symbols=symbols, solve_syms=solve_syms
            ),
        )


@dataclass
class SymbolicCorrelation:
    """Correlation."""

    expr: sympy.Expr
    range: Boolean | None = None


@dataclass
class Correlation:
    """Correlation."""

    expr: Callable[..., Any]
    range: Callable[..., Any] | None
