"""Formatting and display utilities."""

from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any

from IPython.core.display import Markdown, Math
from IPython.display import display
from matplotlib import rc_context
from pandas import DataFrame
from sympy import FiniteSet
from sympy.printing.latex import latex

# * -------------------------------------------------------------------------------- * #
# * DISPLAY


def disp_named(*args: tuple[Any, str]):
    """Display objects with names above them."""
    for elem, name in args:
        display(Markdown(f"##### {name}"))
        display(elem)


def disp_free(title, eqn, **kwargs):
    """Display free symbols."""
    disp(title, eqn, **kwargs)
    disp("Free symbols", FiniteSet(*eqn.rhs.free_symbols), **kwargs)


def disp(title, *exprs, **kwargs):
    """Display equation."""
    print(f"{title}:")  # noqa: T201
    display(*(math_mod(expr, **kwargs) for expr in exprs))


def math_mod(expr, long_frac_ratio=3, **kwargs):
    """Represent expression as LaTeX math."""
    return Math(latex(expr, long_frac_ratio=long_frac_ratio, **kwargs))


# * -------------------------------------------------------------------------------- * #
# * PLOTTING


@contextmanager
def manual_subplot_spacing():
    """Context manager that allows custom spacing of subplots."""
    with rc_context({"figure.autolayout": False}):
        yield


def tex_wrap(df: DataFrame) -> tuple[DataFrame, Mapping[str, str]]:
    """Wrap column titles in LaTeX flags if they contain underscores ($)."""
    mapper: dict[str, str] = {}
    for src_col in df.columns:
        col = f"${handle_subscript(src_col)}$" if "_" in src_col else src_col
        mapper[src_col] = col
    return df.rename(axis="columns", mapper=mapper), mapper


def handle_subscript(val: str) -> str:
    """Wrap everything after the first underscore and replace others with commas."""
    quantity, units = sep_unit(val)
    parts = quantity.split("_")
    quantity = f"{parts[0]}_" + "{" + ",".join(parts[1:]) + "}"
    return add_unit(quantity, units, tex=True)


def add_unit(quantity: str, units: str, tex: bool = False) -> str:
    """Append units to a quantity."""
    if not tex:
        return f"{quantity} ({units})" if units else quantity
    units = units.replace("-", r"{\cdot}")
    return rf"{quantity}\;({units})" if units else quantity


def sep_unit(val: str) -> tuple[str, str]:
    """Split a quantity and its units."""
    quantity, units = val.split(" (")
    units = units.removesuffix(")")
    return quantity, units
