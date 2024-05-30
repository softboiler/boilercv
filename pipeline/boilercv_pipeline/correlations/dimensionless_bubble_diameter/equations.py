"""Equations."""

from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    Param,
    params,
)
from boilercv_pipeline.correlations.models import Params

LATEX_PARAMS = Params[Param].context_model_validate(
    context=Params.get_context(default_keys=params),
    obj={
        "bubble_fourier": {"latex": r"\Fo_\o"},
        "bubble_jakob": {"latex": r"\Ja"},
        "bubble_initial_reynolds": {"latex": r"\Re_\bo"},
        "liquid_prandtl": {"latex": r"\Pr"},
        "dimensionless_bubble_diameter": {"latex": r"\beta"},
        "pi": {"latex": r"\pi"},
    },
)
"""Parameters for function calls."""
SYMPY_SUBS = {arg["sympy"]: name for name, arg in LATEX_PARAMS.items()}
"""Substitutions from SymPy symbolic variables to descriptive names."""
