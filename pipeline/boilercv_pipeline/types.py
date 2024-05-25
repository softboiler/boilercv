"""Types."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Literal, ParamSpec, TypeAlias, TypeVar

from numpydantic import NDArray, Shape
from numpydantic.types import DtypeType, ShapeType

from boilercv_pipeline.annotations import CtxV

if TYPE_CHECKING:
    from boilercv_pipeline.morphs import CtxMorph


ST = TypeVar("ST", bound=ShapeType)
DT = TypeVar("DT", bound=DtypeType)
T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)
P = ParamSpec("P")
K = TypeVar("K")
V = TypeVar("V")
CM = TypeVar("CM", bound="CtxMorph[Any, Any]")

# ? Notebook handling
NbProcess: TypeAlias = Callable[[Path, SimpleNamespace], None]
"""Notebook process."""
Stage: TypeAlias = Literal["large_sources", "sources", "filled"]
"""Stage."""


# ? `numpy` array shapes
AnyShape: TypeAlias = Shape["*"]  # noqa: F722
"""Any shape."""
Vector: TypeAlias = Shape["*"]  # noqa: F722
"""Vector shape."""

# ? Equations
Expectation: TypeAlias = float | NDArray[Vector, float]  # pyright: ignore[reportInvalidTypeArguments]
"""Expectation."""

# ? Recursive
Leaf: TypeAlias = Any
"""Leaf node."""
Node: TypeAlias = Mapping[Any, "Node | Leaf"]
"""General node."""
MutableNode: TypeAlias = MutableMapping[Any, "MutableNode | Leaf"]
"""Mutable general node."""

# ? Contexts
Ctx: TypeAlias = dict[str, "CtxV"]
"""Pydantic context."""
