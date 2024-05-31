"""Pipes."""

from collections.abc import Iterable
from string import whitespace
from typing import Any

import sympy

from boilercv.mappings import replace, replace_pattern, sort_by_keys_pattern
from boilercv.mappings.types.runtime import Repl
from boilercv.morphs.contexts import Context, Defaults, Pipe, compose_context
from boilercv.morphs.morphs import Morph
from boilercv_pipeline.correlations.types import K
from boilercv_pipeline.correlations.types.runtime import KeysPattern, Kind, LocalSymbols
from boilercv_pipeline.equations import keys_pattern
from boilercv_pipeline.types.runtime import SympifyParams, contextualized

identity_equation = sympy.Eq(0, 0, evaluate=False)


def fold_whitespace(i: dict[K, str], defaults: Defaults[K, str]) -> dict[K, str]:
    """Fold whitespace."""
    return replace(
        i,
        (
            Repl[K](src=key, dst=key, find=find, repl=" ")
            for find in whitespace
            for key in defaults.keys
        ),
    )


def set_equation_forms(
    forms: Morph[Kind, str], symbols: LocalSymbols
) -> Morph[Kind, str]:
    """Set equation forms."""
    forms.pipe(
        replace,
        (
            Repl[Kind](src="sympy", dst="sympy", find=find, repl=repl)
            for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
        ),
    ).pipe(
        replace_pattern,
        (
            Repl[Kind](src="sympy", dst="sympy", find=find, repl=repl)
            for sym in symbols
            for find, repl in {
                # ? Symbol split by `(` after first character.
                rf"{sym[0]}\*\({sym[1:]}([^)]+)\)": rf"{sym}\g<1>",
                # ? Symbol split by a `*` after first character.
                rf"{sym[0]}\*{sym[1:]}": rf"{sym}",
                # ? Symbol missing `*` resulting in failed attempt to call it
                rf"{sym}\(": rf"{sym}*(",
            }.items()
        ),
    )
    return forms


def set_latex_forms(forms: Morph[Kind, str]) -> Morph[Kind, str]:
    """Set forms for parameters."""
    if forms["sympy"] and not forms["latex"]:
        forms["latex"] = forms["sympy"]
    forms = forms.pipe(
        replace,
        repls=[
            Repl[Kind](src="latex", dst="sympy", find=k, repl=v)
            for k, v in {r"_\b0": "_bo", r"_\o": "_0", "\\": ""}.items()
        ],
    )
    return forms


def compose_sympify_context(symbols: Iterable[str]) -> Context:
    """Get `sympify` parameters."""
    return compose_context(
        SympifyParams(locals=dict(LocalSymbols.from_iterable(symbols)), evaluate=False)
    )


def get_symbolic_equations(i: dict[str, Any]) -> dict[str, Any]:
    """Get symbolic equations."""
    i["symbolic_equations"] = {
        name: i["equations"][name]["sympy"] for name in i["equations"]
    }
    return i


sort_by_year = Pipe(contextualized(KeysPattern)(sort_by_keys_pattern), keys_pattern)
