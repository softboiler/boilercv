"""Solve equations."""

from pathlib import Path
from re import sub
from tomllib import loads
from warnings import catch_warnings, filterwarnings

import sympy
from cyclopts import App
from loguru import logger
from numpy import finfo
from pydantic import TypeAdapter
from stopit import ThreadingTimeout
from sympy import symbols
from sympy.solvers import solve
from tomlkit import parse
from tqdm import tqdm

from boilercv.morphs import Morph
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.morphs import (
    EQUATIONS_TOML,
    KWDS,
    LOCAL_SYMBOLS,
    SOLUTIONS_TOML,
    EquationSolutions,
)
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    Param,
    Sym,
    params,
    solve_syms,
    syms,
)
from boilercv_pipeline.correlations.types import Equations
from boilercv_pipeline.mappings import filt, sync
from boilercv_pipeline.morphs import Solutions, get_ctx
from boilercv_pipeline.types import Eq, LocalSymbols, Symbol, SympifyParams

SYMS_TO_PARAMS = dict(zip(syms, params, strict=True))
"""Mapping of symbols to parameters."""
SUBS = {sym: KWDS[SYMS_TO_PARAMS[name]] for name, sym in LOCAL_SYMBOLS.items()} | {
    LOCAL_SYMBOLS[k]: v  # pyright: ignore[reportArgumentType]
    for k, v in {"Fo_0": 0, "beta": 0.5}.items()
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
    symbol_names: tuple[str, ...] = syms,
    symbol_subs: tuple[float, ...] = tuple(SUBS.values()),  # pyright: ignore[reportArgumentType]
    solve_syms: tuple[Sym, ...] = solve_syms,
    equations: Path = EQUATIONS_TOML,
    solutions: Path = SOLUTIONS_TOML,
    overwrite: bool = False,
):
    local_syms = dict(
        LocalSymbols(
            zip(
                symbol_names,
                symbols(
                    list(
                        Morph[Param, Sym](dict(zip(params, syms, strict=True))).values()
                    ),
                    nonnegative=True,
                    real=True,
                    finite=True,
                ),
                strict=False,
            )
        )
    )
    subs = dict(zip(syms, symbol_subs, strict=True))
    eqns = Equations.with_ctx(
        loads(equations.read_text("utf-8")),
        get_ctx(Equations.get_morphs(local_symbols=LOCAL_SYMBOLS)),
    )
    solns = EquationSolutions.with_ctx(
        loads(solutions.read_text("utf-8")),
        ctx=get_ctx(
            EquationSolutions.get_morphs(),
            SympifyParams(locals=dict(LOCAL_SYMBOLS), evaluate=False),
        ),
    )
    with solns.thaw_self():
        for name, eq in tqdm(eqns.items()):
            soln = solns[name]
            if not overwrite and eq and filt(soln.model_dump()):
                continue
            with soln.thaw_self():
                for sym in soln.default_keys:
                    soln[sym] = solve_equation(
                        TypeAdapter(Eq).validate_python(eq["sympy"], context=expr_ctx),
                        local_syms[sym],
                        subs,
                    )
                    solns[name] = soln
    solutions.write_text(
        encoding="utf-8",
        data=sync(
            reference=solns.model_dump(mode="json"),
            target=parse(solutions.read_text("utf-8")),
        ).as_string(),
    )


def solve_equation(eq: sympy.Eq, sym: Symbol, subs: dict[Sym, float]) -> Solutions:
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
        result = s.evalf(subs=subs)
        if not result.is_real:
            continue
        if result < finfo(float).eps:
            continue
        soln.solutions.append(s)
    return soln


if __name__ == "__main__":
    logger.info("Start generating symbolic equations.")
    main()
    logger.info("Finish generating symbolic equations.")
