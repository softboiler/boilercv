"""Static type annotations used in {mod}`boilercv_pipeline`."""

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, ParamSpec, Protocol, TypeAlias, TypeVar

from numpydantic import NDArray, Shape

T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)
P = ParamSpec("P")
K = TypeVar("K")
V = TypeVar("V")

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


class Transform(Protocol[T, P, R]):  # noqa: D101
    def __call__(self, i: T, /, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102
