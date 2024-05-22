"""Solve equations."""

from json import loads
from re import sub
from warnings import catch_warnings, filterwarnings

import sympy
from boilercore import syms
from cyclopts import App
from loguru import logger
from numpy import finfo
from stopit import ThreadingTimeout
from sympy import sympify
from sympy.solvers import solve
from tomlkit import dumps, parse
from tqdm import tqdm

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.morphs import (
    EQUATIONS,
    KWDS,
    LOCALS,
    SOLUTIONS,
    SOLUTIONS_TOML,
    BetaSolns,
)
from boilercv_pipeline.models import params
from boilercv_pipeline.morphs import Expr, Soln

SYMS_TO_PARAMS = dict(zip(syms, params, strict=True))
"""Mapping of symbols to parameters."""
SUBS = {sym_: KWDS[SYMS_TO_PARAMS[name]] for name, sym_ in LOCALS.items()} | {
    "beta": 0.5
}
"""Substitutions to check for nonzero solutions."""

APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(overwrite: bool = False):  # noqa: D103
    toml = parse(dumps(SOLUTIONS.model_dump(mode="json")))
    for name, eq in tqdm(
        (name, sympify(eq["sympy"], locals=LOCALS.model_dump(), evaluate=False))
        for name, eq in EQUATIONS.items()
        if not toml.get(name) or overwrite
    ):
        toml[name] = loads(get_solutions(eq).model_dump_json())
    SOLUTIONS_TOML.write_text(
        encoding="utf-8", data=dumps({name: toml[name] for name in sorted(toml)})
    )


def get_solutions(eq: sympy.Eq):
    """Get solutions for an equation."""
    return BetaSolns({
        param: solve_equation(eq, sym)
        for param, sym in ((s, LOCALS[s]) for s in solve_syms)
    })


def solve_equation(eq: sympy.Eq, sym: Expr) -> Soln:
    """Find solution."""
    soln = Soln(solutions=[], warnings=[])
    if eq.lhs is sym and sym not in eq.rhs.free_symbols:
        soln["solutions"].append(eq.rhs)
        return soln
    if eq.rhs is sym and sym not in eq.lhs.free_symbols:
        soln["solutions"].append(eq.lhs)
        return soln
    with (
        ThreadingTimeout(5) as solved,
        catch_warnings(record=True, category=UserWarning) as warnings,
    ):
        filterwarnings("always", category=UserWarning)
        solutions = solve(eq, sym, positive=True, warn=True)
    soln["warnings"].extend(
        sub(r"\s+", " ", w.message.args[0].strip().removeprefix("Warning: "))  # pyright: ignore[reportAttributeAccessIssue]
        for w in warnings
    )
    if not solved:
        return soln
    for s in solutions:
        result = s.evalf(subs=SUBS)
        if not result.is_real:
            continue
        if result < finfo(float).eps:
            continue
        soln["solutions"].append(s)
    return soln


if __name__ == "__main__":
    logger.info("Start generating symbolic equations.")
    main()
    logger.info("Finish generating symbolic equations.")
