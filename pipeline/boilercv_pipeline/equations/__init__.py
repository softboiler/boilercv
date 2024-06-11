"""Equation processing."""

from collections.abc import Callable, Iterable
from pathlib import Path
from re import finditer
from shlex import quote
from typing import cast, get_args

from boilercv.correlations import beta, nusselt
from boilercv.correlations.beta.types import SolveSym as SolveSymBeta
from boilercv.correlations.models import EquationForms, Equations, Forms
from boilercv.correlations.nusselt.types import SolveSym as SolveSymNusselt
from boilercv.correlations.pipes import LocalSymbols
from boilercv.correlations.types import Kind
from boilercv.morphs.contexts import Context, Pipe, make_pipelines
from boilercv.morphs.morphs import Morph

PIPX = Path(".venv") / "scripts" / "pipx"

PNGS = {"beta": beta.PNGS, "nusselt": nusselt.PNGS}

EQUATIONS = {"beta": beta.EQUATIONS_TOML, "nusselt": nusselt.EQUATIONS_TOML}
SOLUTIONS = {"beta": beta.SOLUTIONS_TOML, "nusselt": nusselt.SOLUTIONS_TOML}
EXPECTATIONS = {"beta": beta.EXPECTATIONS_TOML, "nusselt": nusselt.EXPECTATIONS_TOML}

_expectations = {
    "beta": beta.SYMBOL_EXPECTATIONS | {"Fo_0": 0.0},
    "nusselt": nusselt.SYMBOL_EXPECTATIONS | {"Fo_0": 0.0},
}
SUBSTITUTIONS = {
    corr: cast(tuple[tuple[str, float], ...], tuple(expectations.items()))
    for corr, expectations in _expectations.items()
}
SYMS = {
    corr: tuple(expectations.keys()) for corr, expectations in _expectations.items()
}
SOLVE_SYMS = {"beta": get_args(SolveSymBeta), "nusselt": get_args(SolveSymNusselt)}


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


def get_raw_equations_context(symbols: Iterable[str]) -> Context:
    """Get raw equations."""
    forms_context = Forms.get_context()
    forms_context.pipelines[Forms].before = (forms_context.pipelines[Forms].before[0],)
    return Equations[str].get_context(symbols=symbols, forms_context=forms_context)


def sanitize_forms(
    forms,
    symbols,
    sanitizer: Callable[[dict[Kind, str], tuple[str, ...]], Morph[Kind, str]],
) -> EquationForms[str]:
    """Sanitize forms."""
    return EquationForms[str].context_model_validate(
        obj=forms.model_dump(),
        context=EquationForms[str].get_context(
            symbols=symbols,
            forms_context=make_pipelines(
                Forms,
                before=[
                    Forms.get_context().pipelines[Forms].before[0],
                    Pipe(sanitizer, LocalSymbols.from_iterable(symbols)),
                ],
            ),
        ),
    )
