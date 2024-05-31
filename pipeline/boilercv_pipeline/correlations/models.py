"""Bubble collapse correlation models."""

from collections.abc import Iterable
from typing import Any, Generic, NamedTuple, cast

import sympy
from pydantic import Field

from boilercv.morphs.contexts import (
    Context,
    ContextBaseModel,
    ContextMorph,
    Defaults,
    Pipe,
    compose_contexts,
    compose_defaults,
    compose_pipelines,
)
from boilercv_pipeline.correlations.pipes import (
    compose_sympify_context,
    fold_whitespace,
    get_symbolic_equations,
    identity_equation,
    set_equation_forms,
    set_latex_forms,
    sort_by_year,
)
from boilercv_pipeline.correlations.types import K, S
from boilercv_pipeline.correlations.types.runtime import (
    Equation,
    Kind,
    LocalSymbols,
    eqs,
    kinds,
)
from boilercv_pipeline.types.runtime import Eq, Expr


class Forms(ContextMorph[Kind, str]):
    """Forms."""

    @classmethod
    def get_context(cls) -> Context:
        """Get context."""
        return compose_defaults(cls, keys=kinds, value="")


class Equations(ContextMorph[Equation, Forms]):
    """Equations."""

    @classmethod
    def get_context(cls, symbols: Iterable[str]) -> Context:
        """Get context."""
        return compose_contexts(
            compose_defaults(
                cls, keys=eqs, value_model=Forms, value_context=Forms.get_context()
            ),
            compose_pipelines(cls, before=sort_by_year),
            compose_pipelines(
                Forms,
                after=[
                    Pipe(fold_whitespace, Defaults(keys=kinds)),
                    Pipe(set_equation_forms, LocalSymbols.from_iterable(symbols)),
                ],
            ),
        )


class Params(ContextMorph[K, Forms], Generic[K]):
    """Parameters."""

    @classmethod
    def get_context(cls, default_keys: tuple[K, ...]) -> Context:
        """Get Pydantic context."""
        return compose_contexts(
            compose_defaults(cls, keys=default_keys, value_model=Forms),
            compose_pipelines(
                Forms,
                after=[Pipe(fold_whitespace, Defaults(keys=kinds)), set_latex_forms],
            ),
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
    def get_context(cls, symbols: Iterable[str], solve_syms: tuple[S, ...]) -> Context:
        """Get Pydantic context."""
        return compose_defaults(
            cls,
            keys=solve_syms,
            value_model=Solutions,
            value_context=Solutions.get_context(symbols=symbols),
        )


class EquationSolutions(ContextMorph[Equation, SymbolSolutions[S]], Generic[S]):
    """Equation solutions."""

    @classmethod
    def get_context(cls, symbols: Iterable[str], solve_syms: tuple[S, ...]) -> Context:
        """Get Pydantic context."""
        return compose_contexts(
            compose_defaults(
                cls,
                keys=eqs,
                value_model=SymbolSolutions,
                value_context=SymbolSolutions.get_context(
                    symbols=symbols, solve_syms=solve_syms
                ),
            ),
            compose_pipelines(cls, before=sort_by_year),
        )


class SolvedEquations(ContextBaseModel, Generic[S]):
    """Solved equations."""

    equations: Equations
    """Equations."""
    solutions: EquationSolutions[S]
    """Solutions."""
    symbolic_equations: ContextMorph[Equation, Eq]
    """Symbolic form of equations."""

    @classmethod
    def get_context(cls, symbols: Iterable[str], solve_syms: tuple[S, ...]) -> Context:
        """Get Pydantic context."""
        return compose_contexts(
            compose_pipelines(cls, before=get_symbolic_equations),
            Equations.get_context(symbols=symbols),
            EquationSolutions[S].get_context(symbols=symbols, solve_syms=solve_syms),
            compose_contexts(
                compose_defaults(
                    ContextMorph[Equation, Eq],
                    keys=eqs,
                    factory=lambda: identity_equation,
                ),
                compose_pipelines(ContextMorph[Equation, Eq], before=sort_by_year),
                compose_sympify_context(symbols),  # for `Eq`
            ),
        )


class ContextualizedSolutions(NamedTuple, Generic[S]):
    """Contextualized solutions."""

    local_symbols: LocalSymbols
    equations: Equations
    solutions: EquationSolutions[S]
    symbolic_equations: dict[Equation, sympy.Eq]


def contextualize_solutions(
    equations: dict[str, Any],
    solutions: dict[str, Any],
    symbols: tuple[str, ...],
    solve_for: tuple[str, ...],
) -> ContextualizedSolutions[str]:
    """Get equations and their solutions."""
    solved_equations = SolvedEquations.context_model_validate(
        dict(equations=equations, solutions=solutions),
        context=SolvedEquations.get_context(symbols=symbols, solve_syms=solve_for),
    )
    return ContextualizedSolutions(
        local_symbols=LocalSymbols.from_iterable(symbols),
        equations=solved_equations.equations,
        solutions=solved_equations.solutions,
        symbolic_equations=cast(
            dict[Equation, sympy.Eq], dict(solved_equations.symbolic_equations)
        ),
    )
