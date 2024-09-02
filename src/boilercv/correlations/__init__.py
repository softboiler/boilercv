"""Theoretical correlations for bubble lifetimes."""

from collections.abc import Callable
from pathlib import Path
from tomllib import loads
from typing import Any, cast, get_args

import numpy
import sympy
from sympy.logic.boolalg import Boolean

from boilercv.correlations.models import (
    Correlation,
    Equations,
    SolvedEquations,
    SymbolicCorrelation,
)
from boilercv.correlations.types import AnyExpr, Equation, Sym, trivial_expr
from boilercv.morphs.contexts import get_pipeline_context
from boilercv.morphs.types import LiteralGenericAlias

_base = Path(__file__).with_suffix(".toml")
META_TOML = _base.with_stem("meta")
"""Correlation metadata."""
RANGES_TOML = _base.with_stem("ranges")
"""Correlation ranges of applicability."""
INDEPENDENT_VARIABLES = {"Nu_c": "nusselt", "Fo_0": "bubble_fourier"}
"""Independent variables.

Should appear first in positional argument lists to facilitate application of
{func}`~scipy.optimize.curve_fit`.
"""
SYMBOLS = {
    **INDEPENDENT_VARIABLES,
    "Ja": "bubble_jakob",
    "Re_b": "bubble_reynolds",
    "Re_b0": "bubble_initial_reynolds",
    "Pr": "liquid_prandtl",
    "beta": "beta",
    "Pe": "peclet",
    "alpha": "thermal_diffusivity",
    "pi": "pi",
}
"""Symbols.

Independent variables appear first to facilitate application of {func}`~scipy.optimize.curve_fit`.
"""
INDEPENDENT_SYMBOL_LABELS = {"Nu_c": "Nusselt number", "Fo_0": "Bubble Fourier number"}
"""Symbol labels of independent variables."""
SYMBOL_LABELS = {
    **INDEPENDENT_SYMBOL_LABELS,
    "Ja": "Bubble Jakob number",
    "Re_b": "Bubble Reynolds number",
    "Re_b0": "Initial bubble Reynolds number",
    "Pr": "Liquid Prandtl number",
    "beta": "Dimensionless bubble diameter",
    "Pe": "Bubble Peclet number",
    "alpha": "Liquid thermal diffusivity",
    "pi": "pi",
}
"""Symbol labels."""
GROUPS = {
    k: f"Group {v}"
    for k, v in {
        "florschuetz_chao_1965": 1,
        "isenberg_sideman_1970": 3,
        "akiyama_1973": 3,
        "chen_mayinger_1992": 3,
        "zeitoun_et_al_1995": 5,
        "kalman_mori_2002": 3,
        "warrier_et_al_2002": 4,
        "yuan_et_al_2009": 4,
        "lucic_mayinger_2010": 3,
        "kim_park_2011": 3,
        "inaba_et_al_2013": 5,
        "al_issa_et_al_2014": 3,
        "tang_et_al_2016": 3,
    }.items()
}
"""Group numbers for correlations."""


def get_equations(path: Path) -> Equations[AnyExpr]:
    """Get equations."""
    return Equations[AnyExpr].model_validate(
        obj=loads(path.read_text(encoding="utf-8") if path.exists() else "{}"),
        context=get_pipeline_context(
            Equations[AnyExpr].get_context(symbols=get_args(Sym))
        ),
    )


def get_equations_and_solutions(
    equations: Path, solutions: Path, solve_sym: LiteralGenericAlias
) -> dict[Equation, SymbolicCorrelation]:
    """Get correlation equations and their solutions."""
    ranges = get_equations(RANGES_TOML)
    return {
        name: SymbolicCorrelation(
            expr=cast(sympy.Expr, next(iter(soln.values())).solutions[0]),
            range=cast(
                Boolean,
                None if ranges[name].sympy == trivial_expr else ranges[name].sympy,
            ),
        )
        for name, soln in (
            SolvedEquations[solve_sym]
            .model_validate(
                dict(
                    equations=loads(
                        equations.read_text("utf-8") if equations.exists() else ""
                    ),
                    solutions=loads(
                        solutions.read_text("utf-8") if solutions.exists() else ""
                    ),
                ),
                context=get_pipeline_context(
                    SolvedEquations[solve_sym].get_context(
                        symbols=get_args(Sym), solve_syms=get_args(solve_sym)
                    )
                ),
            )
            .solutions
        ).items()
    }


def get_correlations(
    equations: Path, solutions: Path, solve_sym: LiteralGenericAlias
) -> dict[Equation, Correlation]:
    """Get correlations and their ranges."""
    return {
        name: Correlation(
            expr=lambdify_expr(soln.expr),
            range=lambdify_expr(soln.range) if soln.range else None,
        )
        for name, soln in get_equations_and_solutions(
            equations=equations, solutions=solutions, solve_sym=solve_sym
        ).items()
    }


def lambdify_expr(expr: sympy.Basic) -> Callable[..., Any]:
    """Get symbolic functions."""
    return sympy.lambdify(
        expr=expr,
        modules=numpy,
        # Make `args` in order of `SYMBOLS` so `scipy.optimize.curve_fit` gets x's first
        args=[s for s in SYMBOLS if s in {s.name for s in expr.free_symbols}],  # pyright: ignore[reportAttributeAccessIssue]
    )
