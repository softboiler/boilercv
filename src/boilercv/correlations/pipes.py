"""Pipes."""

from collections import UserDict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, dataclass
from functools import wraps
from re import Pattern, compile
from string import whitespace
from typing import Any

from sympy import Symbol, symbols

from boilercv.correlations.types import CVL, Kind, P, Ps, R, SympifyParams, Transform
from boilercv.mappings import Repl, replace, replace_pattern, sort_by_keys_pattern
from boilercv.morphs.contexts import (
    Context,
    ContextValue,
    Defaults,
    Pipe,
    compose_context,
)
from boilercv.morphs.morphs import Morph


def fold_whitespace(
    forms: dict[Kind, str], defaults: Defaults[Kind, str]
) -> Morph[Kind, str]:
    """Fold whitespace."""
    return (
        Morph[Kind, str](forms)
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
        .morph_pipe(lambda forms: {k: v.strip() for k, v in forms.items()})
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


@dataclass
class KeysPattern(ContextValue):
    """Keys pattern."""

    pattern: Pattern[str]
    groups: Iterable[str]
    apply_to_match: Callable[[list[str]], Any] = str
    message: str = "Match not found when sorting."


def contextualized(context_value_type: type[CVL]):
    """Contextualize function on `context_value_type`."""

    def contextualizer(f: Transform[P, Ps, R]) -> Callable[[P, CVL], R]:
        @wraps(f)
        def unpack_kwds(v: P, context_value: CVL) -> R:
            if not isinstance(context_value, context_value_type):
                raise ValueError(  # noqa: TRY004 so Pydantic catches it
                    f"Expected context value type '{context_value_type}', got '{type(context_value)}."
                )
            context_mapping = (
                context_value
                if isinstance(context_value, Mapping)
                else asdict(context_value)
            )
            return f(v, **context_mapping)  # pyright: ignore[reportCallIssue]

        return unpack_kwds

    return contextualizer


equation_name_pattern = compile(
    r"""(?xm)^  # x: verbose, m: multiline, ^: begin, always use multiline https://web.archive.org/web/20240429145610/https://sethmlarson.dev/regex-$-matches-end-of-string-or-newline
    (?P<author>[\w_]+?)  # lazy so year is leftmost match
    _(?P<sort>  # sort on year and optional equation number
        (?P<year>\d{4})  # year must be four digits
        (?:_(?P<num>[\d_]+))?  # optionally, multiple equations from one paper
    )
    $"""
)


def apply_to_match(groups: list[str]) -> tuple[int, int, str]:
    """Apply to match."""
    first, *rest = groups[0].split("_")
    year = int(first)
    num = int(rest[0]) if rest else 0
    author = groups[1]
    return year, num, author


sort_by_year = Pipe(
    contextualized(KeysPattern)(sort_by_keys_pattern),
    KeysPattern(
        pattern=equation_name_pattern,
        groups=["sort", "author"],
        apply_to_match=apply_to_match,
        message="Couldn't find year in equation identifier '{key}' when sorting.",
    ),
)
