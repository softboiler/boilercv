"""Theoretical correlations for bubble lifetimes."""

from pathlib import Path
from typing import Any

from boilercv.morphs.contexts import LocalSymbols, get_context_value
from boilercv_pipeline.correlations.models import Equations, EquationSolutions
from boilercv_pipeline.correlations.types import ContextualizedSolutions
from boilercv_pipeline.types.runtime import SympifyParams

PNGS = Path("data/dimensionless_bubble_diameter_equation_pngs")
"""Equation PNGs."""
PIPX = Path(".venv") / "scripts" / "pipx"
"""Escaped path to `pipx` executable suitable for `subprocess.run` invocation."""


def get_solutions_in_context(
    equations: dict[str, Any],
    solutions: dict[str, Any],
    symbols: tuple[str, ...],
    solve_for: tuple[str, ...],
) -> ContextualizedSolutions:
    """Get equations and their solutions."""
    context = EquationSolutions.get_context(symbols=symbols, solve_syms=solve_for)
    sympify_params = get_context_value(SympifyParams, context)
    if not sympify_params:
        raise ValueError("Missing `SympifyParams` in context.")
    return ContextualizedSolutions(
        local_symbols=LocalSymbols.from_iterable(symbols),
        equations=Equations.model_validate(
            equations, context=Equations.get_context(symbols=symbols)
        ),
        solutions=EquationSolutions[str].model_validate(solutions, context=context),
        sympify_params=sympify_params,
    )
