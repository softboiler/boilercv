"""Solve equations."""

from re import sub
from tomllib import loads
from warnings import catch_warnings, filterwarnings

import sympy
from cyclopts import App
from loguru import logger
from numpy import finfo
from stopit import ThreadingTimeout
from sympy.solvers import solve
from tomlkit import TOMLDocument, parse
from tqdm import tqdm

from boilercv.correlations.models import Solutions, SolvedEquations, SymbolSolutions
from boilercv.correlations.pipes import LocalSymbols
from boilercv.correlations.types import Corr, Equation, trivial
from boilercv.mappings import filt, sync
from boilercv.morphs.contexts import Context
from boilercv.morphs.morphs import Morph
from boilercv_pipeline.equations import EQUATIONS, SOLUTIONS, SOLVE_SYMS, SUBSTITUTIONS

TIMEOUT = 5
"""Solver timeout in seconds."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta", overwrite: bool = False):  # noqa: D103
    equations = EQUATIONS[corr]
    solutions = SOLUTIONS[corr]
    substitutions = SUBSTITUTIONS[corr]
    solve_for = SOLVE_SYMS[corr]

    logger.info("Start generating symbolic equations.")

    # ? Produce equations and solutions model
    eqns_content = loads(equations.read_text("utf-8") if equations.exists() else "")
    solns_content = solutions.read_text("utf-8") if solutions.exists() else ""
    symbols = tuple(dict(substitutions).keys())
    context = SolvedEquations[str].get_context(symbols=symbols, solve_syms=solve_for)
    model = SolvedEquations[str].context_model_validate(
        dict(equations=eqns_content, solutions=loads(solns_content)), context=context
    )

    # ? Solve equations
    solutions.write_text(
        encoding="utf-8",
        data=(
            sync(
                reference=model.solutions.morph_cpipe(
                    solve_equations,
                    context,
                    equations={
                        name: eq["sympy"]
                        for name, eq in model.equations.model_dump().items()
                    },
                    substitutions=dict(substitutions),
                    solve_for=solve_for,
                    overwrite=overwrite,
                    symbols=LocalSymbols.from_iterable(symbols),
                    context=context,
                ).model_dump(mode="json"),
                target=TOMLDocument() if overwrite else parse(solns_content),
            )
        ).as_string(),
    )
    logger.info("Finish generating symbolic equations.")


def solve_equations(
    solutions: Morph[Equation, SymbolSolutions[str]],
    equations: dict[Equation, sympy.Eq],
    substitutions: dict[str, float],
    solve_for: tuple[str, ...],
    overwrite: bool,
    symbols: LocalSymbols,
    context: Context,
) -> Morph[Equation, SymbolSolutions[str]]:
    """Solve equations."""
    for name, eq in tqdm(equations.items()):
        filtered_solutions = filt(solutions[name].model_dump())
        if eq == trivial or (not overwrite and filtered_solutions):
            continue
        solutions[name] = solutions[name].morph_cpipe(
            solve_equation,
            context,
            equation=eq,
            substitutions=substitutions,
            solve_for=solve_for,
            symbols=symbols,
        )
    return solutions


def solve_equation(
    solutions: dict[str, Solutions],
    equation: sympy.Eq,
    substitutions: dict[str, float],
    solve_for: tuple[str, ...],
    symbols: LocalSymbols,
) -> dict[str, Solutions]:
    """Solve equation."""
    for sym in solve_for:
        solutions[sym] = solve_for_symbol(
            eq=equation, sym=symbols[sym], substitutions=substitutions
        )
    return solutions


def solve_for_symbol(
    eq: sympy.Eq, sym: sympy.Symbol, substitutions: dict[str, float]
) -> Solutions:
    """Solve equation."""
    soln = Solutions()
    if eq.lhs is sym and sym not in eq.rhs.free_symbols:
        soln.solutions.append(eq.rhs)
        return soln
    if eq.rhs is sym and sym not in eq.lhs.free_symbols:
        soln.solutions.append(eq.lhs)
        return soln
    with (
        ThreadingTimeout(TIMEOUT) as solved,
        catch_warnings(record=True, category=UserWarning) as warnings,
    ):
        filterwarnings("always", category=UserWarning)
        solutions = solve(eq, sym, positive=True, warn=True)
    soln.warnings.extend(
        sub(r"\s+", " ", w.message.args[0].strip().removeprefix("Warning: "))  # pyright: ignore[reportAttributeAccessIssue]
        for w in warnings
    )
    if not solved:
        soln.warnings.append(f"Unable to find solution within {TIMEOUT} seconds.")
        return soln
    for s in solutions:
        result = s.evalf(subs=substitutions)
        if not result.is_real:
            continue
        if result < finfo(float).eps:
            continue
        soln.solutions.append(s)
    return soln


if __name__ == "__main__":
    main()
