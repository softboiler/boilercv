"""Nusselt number correlations for subcooled boiling bubble collapse."""

from pathlib import Path
from tomllib import loads
from typing import get_args

from numpy import linspace, pi

from boilercv.correlations.models import Equations, Expectations
from boilercv.correlations.nusselt.types import Sym
from boilercv.correlations.types import Eq, Kind
from boilercv.mappings import Repl

base = Path(__file__).with_suffix(".toml")
EQUATIONS_TOML = base.with_stem("equations")
"""TOML file with equations."""
EXPECTATIONS_TOML = base.with_stem("expectations")
"""TOML file with expectations."""
SOLUTIONS_TOML = base.with_stem("solutions")
"""TOML file with solutions."""
LATEX_REPLS = tuple(
    Repl[Kind](src="latex", dst="latex", find=find, repl=repl)
    for find, repl in {"{0}": r"\o", "{b0}": r"\b0"}.items()
)
"""Replacements to make after parsing LaTeX from PNGs."""
SYMBOL_EXPECTATIONS = Expectations[Sym].context_model_validate(
    obj={
        "Fo_0": linspace(start=0.0, stop=5.0e-3, num=10),
        "Ja": 1.0,
        "Re_b0": 100.0,
        "Pr": 1.0,
        "beta": 0.5,
        "pi": pi,
    },
    context=Expectations[Sym].get_context(),
)
"""Common keyword arguments applied to correlations."""


def get_equations() -> Equations[Eq]:  # noqa: D103
    return Equations[Eq].context_model_validate(
        obj=loads(EQUATIONS_TOML.read_text("utf-8") if EQUATIONS_TOML.exists() else ""),
        context=Equations[Eq].get_context(symbols=get_args(Sym)),
    )
