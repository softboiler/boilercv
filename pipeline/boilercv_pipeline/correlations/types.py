"""Types."""

from typing import NamedTuple

from boilercv.morphs.contexts import LocalSymbols
from boilercv_pipeline.correlations.models import Equations, EquationSolutions
from boilercv_pipeline.types.runtime import SympifyParams


class ContextualizedSolutions(NamedTuple):
    """Contextualized solutions."""

    local_symbols: LocalSymbols
    equations: Equations
    solutions: EquationSolutions[str]
    sympify_params: SympifyParams
