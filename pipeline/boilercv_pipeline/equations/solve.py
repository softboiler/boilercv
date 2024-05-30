"""Solve equations."""

from pathlib import Path
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

from boilercv.mappings import filt, sync
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    EQUATIONS_TOML,
    KWDS,
    LOCAL_SYMBOLS,
    SOLUTIONS_TOML,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    params,
    solve_syms,
    syms,
)
from boilercv_pipeline.correlations.models import (
    Solutions,
    contextualize_solutions,
    identity_equation,
)

SYMS_TO_PARAMS = dict(zip(syms, params, strict=True))
"""Mapping of symbols to parameters."""
SUBS = {sym: KWDS[SYMS_TO_PARAMS[name]] for name, sym in LOCAL_SYMBOLS.items()} | {  # pyright: ignore[reportArgumentType]
    LOCAL_SYMBOLS[k]: v for k, v in {"Fo_0": 0, "beta": 0.5}.items()
}
"""Substitutions to check for nonzero solutions."""
TIMEOUT = 5
"""Solver timeout in seconds."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(  # noqa: D103
    equations: Path = EQUATIONS_TOML,
    solutions: Path = SOLUTIONS_TOML,
    symbols: tuple[str, ...] = syms,
    substitutions: tuple[float, ...] = tuple(SUBS.values()),  # pyright: ignore[reportArgumentType]
    solve_for: tuple[str, ...] = solve_syms,
    overwrite: bool = False,
):
    logger.info("Start generating symbolic equations.")
    solutions_content = solutions.read_text("utf-8") if solutions.exists() else ""
    syms, _, solns, eqns = contextualize_solutions(
        equations=loads(equations.read_text("utf-8") if equations.exists() else ""),
        solutions=loads(solutions_content),
        symbols=symbols,
        solve_for=solve_for,
    )
    subs = dict(zip(syms.keys(), substitutions, strict=True))
    for name, eq in tqdm(eqns.items()):
        if not overwrite and eq != identity_equation and filt(solns[name].model_dump()):
            continue
        for sym in solve_for:
            solns[name][sym] = solve_equation(eq=eq, sym=syms[sym], substitutions=subs)
    solutions.write_text(
        encoding="utf-8",
        data=(
            sync(
                reference=solns.model_dump(mode="json"),
                target=TOMLDocument() if overwrite else parse(solutions_content),
            )
        ).as_string(),
    )
    logger.info("Finish generating symbolic equations.")


def solve_equation(
    eq: sympy.Eq, sym: sympy.Symbol, substitutions: dict[str, float]
) -> Solutions:
    """Find solution."""
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
