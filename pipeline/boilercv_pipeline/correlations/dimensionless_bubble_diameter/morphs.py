"""Morphs."""

from pathlib import Path
from tomllib import loads

from numpy import linspace, pi
from sympy import symbols
from tomlkit import parse

from boilercv.morphs import Morph
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import (
    Param,
    Sym,
    params,
    solve_syms,
    syms,
)
from boilercv_pipeline.correlations.types import Equation, Equations, FormsRepl, eqs
from boilercv_pipeline.morphs import CtxMorph, Solutions, get_ctx, set_defaults
from boilercv_pipeline.types import (
    Defaults,
    Expectation,
    LocalSymbols,
    Morphs,
    Pipe,
    SympifyParams,
)

base = Path(__file__).with_suffix(".toml")
EQUATIONS_TOML = base.with_stem("equations")
"""TOML file with equations."""
EXPECTATIONS_TOML = base.with_stem("expectations")
"""TOML file with expectations."""
SOLUTIONS_TOML = base.with_stem("solutions")
"""TOML file with solutions."""
EXPECTATIONS = parse(EXPECTATIONS_TOML.read_text("utf-8"))
"""Expected results for the response of each correlation to `KWDS`."""
MAKE_RAW = {'"': "'", r"\\": "\\"}
"""Replacement to turn escaped characters back to their raw form. Should be last."""
LATEX_REPLS = tuple(
    FormsRepl(src="latex", dst="latex", find=find, repl=repl)
    for find, repl in {"{0}": r"\o", "{b0}": r"\b0"}.items()
)
"""Replacements to make after parsing LaTeX from PNGs."""
KWDS = Morph[Param, Expectation]({
    "bubble_fourier": linspace(start=0.0, stop=5.0e-3, num=10),
    "bubble_jakob": 1.0,
    "bubble_initial_reynolds": 100.0,
    "liquid_prandtl": 1.0,
    "dimensionless_bubble_diameter": 1.0,
    "pi": pi,
})
"""Common keyword arguments applied to correlations.

A single test condition has been chosen to exercise each correlation across as wide of a
range as possible without returning `np.nan` values. This is done as follows:

- Let `bubble_initial_reynolds`,
`liquid_prandtl`, and `bubble_jakob` be 100.0, 1.0, and 1.0, respectively.
- Apply the correlation `dimensionless_bubble_diameter_tang_et_al_2016` with
`bubble_fourier` such that the `dimensionless_bubble_diameter` is very close to zero.
This is the correlation with the most rapidly vanishing value of
`dimensionless_bubble_diameter`.
- Choose ten linearly-spaced points for `bubble_fourier` between `0` and the maximum
`bubble_fourier` just found.
"""


class BetaSolutions(CtxMorph[Sym, Solutions]):
    """Dimensionless bubble diameter solutions."""

    @classmethod
    def get_morphs(cls) -> Morphs:
        """Get morphs."""
        return Morphs({
            BetaSolutions: [
                Pipe(
                    set_defaults,
                    Defaults(default_keys=solve_syms, default_factory=Solutions),
                )
            ]
        })


class EquationSolutions(CtxMorph[Equation, BetaSolutions], foo="bar"):
    """Equation solutions."""

    @classmethod
    def get_morphs(cls) -> Morphs:
        """Get morphs for {class}`Equations`."""
        return Morphs(
            {
                Equations: [
                    Pipe(
                        set_defaults,
                        Defaults(default_keys=eqs, default_factory=BetaSolutions),
                    )
                ]
            }
            | BetaSolutions.get_morphs()
        )


LOCAL_SYMBOLS = LocalSymbols(
    zip(
        syms,
        symbols(
            list(Morph[Param, Sym](dict(zip(params, syms, strict=True))).values()),
            nonnegative=True,
            real=True,
            finite=True,
        ),
        strict=False,
    )
)
"""Local variables."""
SOLUTIONS = EquationSolutions.with_ctx(
    loads(SOLUTIONS_TOML.read_text("utf-8")),
    ctx=get_ctx(
        EquationSolutions.get_morphs(),
        SympifyParams(locals=dict(LOCAL_SYMBOLS), evaluate=False),
    ),
)
"""Solutions."""
EQUATIONS = Equations.with_ctx(
    loads(EQUATIONS_TOML.read_text("utf-8")),
    get_ctx(Equations.get_morphs(local_symbols=LOCAL_SYMBOLS)),
)
