"""Data column model."""

from dataclasses import dataclass, field
from functools import cached_property
from re import search
from typing import Any, NamedTuple

from pandas import DataFrame
from pydantic import BaseModel

from boilercv_pipeline.models.column import types as types  # noqa: PLC0414
from boilercv_pipeline.models.column.types import P, Ps, R, SupportsMul_T
from boilercv_pipeline.units import U


class Parts(NamedTuple):
    """Label parts."""

    sym: str
    sub: str
    unit: str


def get_parts(string: str) -> Parts:
    """Get parts of a label."""
    if m := search(
        r"^(?P<sym>[^_\()]+)(?P<sub>_[^\s]+)?\s?\(?(?P<unit>[^)]+)?\)?$", string
    ):
        return Parts(
            m["sym"].strip(),
            (m["sub"] or "").removeprefix("_").strip(),
            (m["unit"] or "").strip(),
        )
    else:
        raise ValueError(f"Invalid column label: {string}")


def get_name(p: Parts) -> str:
    """Get name from parts."""
    if p.sym and p.sub and p.unit:
        return f"{p.sym}_{p.sub} ({p.unit})"
    return f"{p.sym} ({p.unit})" if p.sym and p.unit else p.sym


def get_latex(p: Parts) -> str:
    """Get LaTeX-wrapped name from parts."""
    label = p.sym
    if p.sub:
        label = f"{label}_{{{p.sub}}}"
    if p.unit:
        label = rf"{label}\ \left({p.unit}\right)"
    return rf"$\mathsf{{{label}}}$"


@dataclass
class Col:
    """Column."""

    sym: str = ""
    unit: str = ""
    sub: str = ""
    raw: str = ""

    def __post_init__(self):
        """Post-init."""
        self.raw = self.raw or get_name(Parts(self.sym, self.sub, self.unit))
        orig = self.sym
        if "_" in orig:
            if self.sub:
                raise ValueError(
                    f"'sub={self.sub}' given but 'sym={orig}' may already have a subscript."
                )
            p = get_parts(orig)
            self.sym, self.sub, self.unit = p.sym, p.sub, self.unit or p.unit
        if "(" in orig:
            if "_" not in orig and self.unit:
                raise ValueError(
                    f"'unit={self.unit}' given but 'sym={orig}' may already have units."
                )
            p = get_parts(orig)
            self.sym, self.sub, self.unit = p.sym, self.sub, p.unit
        self.unit = f"°{self.unit}" if self.unit == "C" else self.unit

    def __call__(self) -> str:
        """Get canonical name."""
        return self.latex

    @cached_property
    def latex(self) -> str:
        """LaTeX name."""
        return get_latex(Parts(self.sym, self.sub, self.unit))

    @property
    def without_subscript(self) -> str:
        """Canonical name without subscript."""
        return Col(sym=self.sym, unit=self.unit)()

    @classmethod
    def from_col(cls, col: "Col") -> "Col":
        """Build a column from a column."""
        return cls(col.sym, col.sub, col.unit, col.raw)


def transform(
    v: P,
    src: Col,
    dst: Col,
    f: types.Transform[P, R, Ps],
    /,
    *args: Ps.args,
    **kwds: Ps.kwargs,
) -> R:
    """Transform."""
    return f(v, src, dst, *args, **kwds)


def scale(v: SupportsMul_T, s: SupportsMul_T, src: Col, dst: Col) -> SupportsMul_T:
    """Scale."""
    return transform(v, src, dst, lambda v, src, dst: v * s)


@dataclass
class Transform:
    """Column transformer."""

    f: types.Transform[Any, Any, Any] = lambda v, _src, _dst: v
    args: tuple[Any] = field(default_factory=tuple)
    kwds: dict[str, Any] = field(default_factory=dict)


@dataclass
class LinkedCol(Col):
    """Column linked to a source."""

    source: Col = field(default_factory=Col)

    def rename(self, df: DataFrame) -> DataFrame:
        """Rename this column."""
        return df.rename(columns={self.source.raw: self()})

    def convert(self, df: DataFrame) -> DataFrame:
        """Convert this column."""
        return U.convert(df[[self.source()]], self.source.unit, self.unit)


@dataclass
class IdentityCol(LinkedCol):
    """Column with a source the same as itself."""

    def __post_init__(self):
        super().__post_init__()
        self.source = Col(self.raw)


def rename(df: DataFrame, cols: list[LinkedCol]) -> DataFrame:
    """Rename."""
    return df.rename(columns={col.source.raw: col() for col in cols})


def convert(df: DataFrame, cols: list[LinkedCol]) -> DataFrame:
    """Convert."""
    return df.assign(**{col(): col.convert(df) for col in cols})


class _Kind(BaseModel):
    """Kind of column."""

    idx: str = "idx"


Kind = _Kind()
"""Kind of column."""