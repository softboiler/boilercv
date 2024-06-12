"""Nusselt number correlations for subcooled boiling bubble collapse."""

from pathlib import Path

from numpy import linspace, pi

from boilercv import correlations
from boilercv.correlations.models import Correlation, Expectations, SymbolicCorrelation
from boilercv.correlations.nusselt.types import SolveSym
from boilercv.correlations.types import Equation, Sym

PNGS = Path("data/png_equations_nusselt")
"""Equation PNGs."""

_base = Path(__file__).with_suffix(".toml")

EQUATIONS_TOML = _base.with_stem("equations")
"""TOML file with equations."""
EXPECTATIONS_TOML = _base.with_stem("expectations")
"""TOML file with expectations."""
SOLUTIONS_TOML = _base.with_stem("solutions")
"""TOML file with solutions."""
SYMBOL_EXPECTATIONS = Expectations[Sym].context_model_validate(
    obj={
        "Nu_c": 1.0,
        "Fo_0": linspace(start=0.0, stop=5.0e-3, num=10),
        "Ja": 1.0,
        "Re_b0": 100.0,
        "Pr": 1.0,
        "beta": 0.5,
        "alpha": 1.0,
        "pi": pi,
    },
    context=Expectations[Sym].get_context(),
)
"""Common keyword arguments applied to correlations."""


def get_equations_and_solutions() -> dict[Equation, SymbolicCorrelation]:
    """Get correlations."""
    return correlations.get_equations_and_solutions(
        EQUATIONS_TOML, SOLUTIONS_TOML, SolveSym
    )


def get_correlations() -> dict[Equation, Correlation]:
    """Get correlations."""
    return correlations.get_correlations(EQUATIONS_TOML, SOLUTIONS_TOML, SolveSym)
