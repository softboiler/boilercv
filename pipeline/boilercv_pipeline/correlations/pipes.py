"""Pipes."""

from collections import UserDict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from re import Pattern, compile
from string import whitespace
from typing import Any

from sympy import Symbol, symbols

from boilercv.mappings import Repl, replace, replace_pattern, sort_by_keys_pattern
from boilercv.morphs.contexts import (
    Context,
    ContextValue,
    Defaults,
    Pipe,
    compose_context,
)
from boilercv.morphs.morphs import Morph
from boilercv_pipeline.correlations.types import Kind
from boilercv_pipeline.types import SympifyParams, contextualized


def fold_whitespace(
    forms: Morph[Kind, str], defaults: Defaults[Kind, str]
) -> Morph[Kind, str]:
    """Fold whitespace."""
    return (
        forms.model_validate(obj=forms)
        .morph_pipe(
            replace,
            (
                Repl[Kind](src=key, dst=key, find=find, repl=" ")
                for find in whitespace
                for key in defaults.keys
            ),
        )
        .morph_pipe(
            replace_pattern,
            (
                Repl[Kind](src=key, dst=key, find=r"\s+", repl=r" ")
                for key in defaults.keys
            ),
        )
    )


class LocalSymbols(UserDict[str, Symbol], ContextValue):
    """Local symbols."""

    @classmethod
    def from_iterable(cls, syms: Iterable[str]):
        """Create from an iterable of symbols."""
        return cls(
            zip(
                syms,
                symbols(syms, nonnegative=True, real=True, finite=True),
                strict=True,
            )
        )


def set_equation_forms(
    forms: Morph[Kind, str], symbols: LocalSymbols
) -> Morph[Kind, str]:
    """Set equation forms."""
    return (
        forms.model_validate(obj=forms)
        .morph_pipe(
            replace,
            (
                Repl[Kind](src="sympy", dst="sympy", find=find, repl=repl)
                for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
            ),
        )
        .morph_pipe(
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
    )


def set_latex_forms(forms: Morph[Kind, str]) -> Morph[Kind, str]:
    """Set forms for parameters."""
    if forms["sympy"] and not forms["latex"]:
        forms["latex"] = forms["sympy"]
    forms = forms.morph_pipe(
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


equation_name_pattern = compile(
    r"""(?xm)^  # x: verbose, m: multiline, ^: begin, always use multiline https://web.archive.org/web/20240429145610/https://sethmlarson.dev/regex-$-matches-end-of-string-or-newline
    (?P<author>[\w_]+?)  # lazy so year is leftmost match
    _(?P<sort>  # sort on year and optional equation number
        (?P<year>\d{4})  # year must be four digits
        (?:_(?P<num>[\d_]+))?  # optionally, multiple equations from one paper
    )
    $"""  # end), group="", message=""),
)


@dataclass
class KeysPattern(ContextValue):
    """Keys pattern."""

    pattern: Pattern[str]
    group: str
    apply_to_match: Callable[[str], Any] = str
    message: str = "Match not found when sorting."


keys_pattern = KeysPattern(
    pattern=equation_name_pattern,
    group="sort",
    apply_to_match=lambda i: [int(n) for n in i.split("_")],
    message="Couldn't find year in equation identifier '{key}' when sorting.",
)

sort_by_year = Pipe(contextualized(KeysPattern)(sort_by_keys_pattern), keys_pattern)
