"""Equation processing."""

from collections.abc import Callable, Iterable
from pathlib import Path
from re import finditer
from shlex import quote
from sys import executable
from typing import cast, get_args

from boilercv.correlations import RANGES_TOML, SYMBOLS, beta, nusselt
from boilercv.correlations.beta.types import SolveSym as SolveSymBeta
from boilercv.correlations.models import (
    Correlation,
    EquationForms,
    Equations,
    Expectations,
    Forms,
    SymbolicCorrelation,
)
from boilercv.correlations.nusselt.types import SolveSym as SolveSymNusselt
from boilercv.correlations.pipes import LocalSymbols
from boilercv.correlations.types import Corr, Equation, Kind, Range, Sym
from boilercv.morphs import Morph
from boilercv.pipelines import make_pipelines
from boilercv.pipelines.contexts import PipelineCtxDict, get_pipeline_context
from boilercv.pipes import Pipe

SYMS = tuple(SYMBOLS.keys())
PIPX = Path(executable).parent / "pipx"
PNGS: dict[Corr, Path] = {"beta": beta.PNGS, "nusselt": nusselt.PNGS}
EQUATIONS: dict[Corr | Range, Path] = {
    "beta": beta.EQUATIONS_TOML,
    "nusselt": nusselt.EQUATIONS_TOML,
    "range": RANGES_TOML,
}
SOLUTIONS: dict[Corr, Path] = {
    "beta": beta.SOLUTIONS_TOML,
    "nusselt": nusselt.SOLUTIONS_TOML,
}
EXPECTATIONS: dict[Corr, Path] = {
    "beta": beta.EXPECTATIONS_TOML,
    "nusselt": nusselt.EXPECTATIONS_TOML,
}
SUBSTITUTIONS: dict[Corr, tuple[tuple[str, float], ...]] = {
    corr: cast(tuple[tuple[str, float], ...], tuple(expectations.items()))
    for corr, expectations in cast(
        dict[Corr, Expectations[Sym]],
        {
            "beta": beta.SYMBOL_EXPECTATIONS | {"Fo_0": 0.0},
            "nusselt": nusselt.SYMBOL_EXPECTATIONS | {"Fo_0": 0.0},
        },
    ).items()
}
SOLVE_SYMS: dict[Corr, tuple[str, ...]] = {
    "beta": get_args(SolveSymBeta),
    "nusselt": get_args(SolveSymNusselt),
}
EQUATIONS_AND_SOLUTIONS: dict[
    Corr, Callable[[], dict[Equation, SymbolicCorrelation]]
] = {
    "beta": beta.get_equations_and_solutions,
    "nusselt": nusselt.get_equations_and_solutions,
}
CORRELATIONS: dict[Corr, Callable[[], dict[Equation, Correlation]]] = {
    "beta": beta.get_correlations,
    "nusselt": nusselt.get_correlations,
}


def escape(path: Path) -> str:
    """Escape path for running subprocesses."""
    return quote(path.as_posix())


def make_raw(content: str):
    """Convert escaped strings to raw strings."""
    for match in finditer(r'"[^"]*"', content):
        old_eq = new_eq = match.group()
        for old, new in {'"': "'", r"\\": "\\"}.items():
            new_eq = new_eq.replace(old, new)
        content = content.replace(old_eq, new_eq)
    return content


def get_raw_equations_context(symbols: Iterable[str]) -> PipelineCtxDict:
    """Get raw equations."""
    forms_context = Forms.get_context()
    forms_context.pipelines[Forms].before = (forms_context.pipelines[Forms].before[0],)
    return get_pipeline_context(
        Equations[str].get_context(symbols=symbols, forms_context=forms_context)
    )


def sanitize_forms(
    forms,
    symbols,
    sanitizer: Callable[[dict[Kind, str], tuple[str, ...]], Morph[Kind, str]],
) -> EquationForms[str]:
    """Sanitize forms."""
    return EquationForms[str].model_validate(
        obj=forms.model_dump(),
        context=get_pipeline_context(
            EquationForms[str].get_context(
                symbols=symbols,
                forms_context=make_pipelines(
                    Forms,
                    before=[
                        Forms.get_context().pipelines[Forms].before[0],
                        Pipe(sanitizer, LocalSymbols.from_iterable(symbols)),
                    ],
                ),
            )
        ),
    )
