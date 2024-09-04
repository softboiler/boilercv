"""Data column model."""

from dataclasses import dataclass
from re import search
from typing import Any

from pandas import DataFrame
from pydantic import BaseModel


def get_unit(unit: str) -> str:
    """Get unit label."""
    return f"°{unit}" if unit == "C" else unit


def get_parts(label: str) -> tuple[str, str, str]:
    """Get parts of a label."""
    if m := search(
        r"^(?P<sym>[^_\()]+)(?P<sub>_[^\s]+)?\s?\(?(?P<unit>[^)]+)?\)?$", label
    ):
        return (
            m["sym"].strip(),
            (m["sub"] or "").removeprefix("_").strip(),
            (m["unit"] or "").strip(),
        )
    return label, "", ""


def get_label(sym: str, sub: str, unit: str) -> str:
    """Get label."""
    if sym and sub and unit:
        return f"{sym}_{sub} ({unit})"
    return f"{sym} ({unit})" if sym and unit else sym


def get_latex(sym: str, sub: str, unit: str) -> str:
    """Get LaTeX label."""
    if sub:
        sym = f"{sym}_{{{sub}}}"
    if unit:
        sym = rf"{sym}\ \left({unit}\right)"
    return rf"$\mathsf{{{sym}}}$"


@dataclass
class Col:
    """Column transformation."""

    src: str
    dst: str = ""
    unit: str = ""
    dst_unit: str = ""
    scale: float = 1
    latex: str = ""
    df: str = ""
    ylabel: str = ""

    def __call__(self) -> Any:
        """Return the canonical label."""
        return self.latex

    def __post_init__(self):
        src_sym, src_sub, src_unit = get_parts(self.src)
        self.unit = get_unit(self.unit or src_unit)

        self.dst = self.dst or get_label(src_sym, src_sub, self.unit)
        dst_sym, dst_sub, dst_unit = get_parts(self.dst)
        self.dst_unit = get_unit(self.dst_unit) or dst_unit or self.unit
        self.dst = get_label(dst_sym, dst_sub, self.dst_unit)
        self.ylabel = get_latex(dst_sym, "", self.dst_unit)

        self.latex = self.latex or get_latex(dst_sym, dst_sub, self.dst_unit)
        self.df = self.df or self.dst


class _Kind(BaseModel):
    """Kind of column."""

    idx: str = "idx"


Kind = _Kind()
"""Kind of column."""


def transform_cols(df: DataFrame, cols: list[Col], drop: bool = True) -> DataFrame:
    """Transform dataframe columns."""
    df = df.assign(**{
        col.dst: df[col.src] if col.scale == 1 else df[col.src] * col.scale
        for col in cols
    })
    return df[[col.dst for col in cols]] if drop else df
