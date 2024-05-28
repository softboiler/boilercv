"""Static type annotations used in {mod}`boilercv_pipeline`."""

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Literal, TypeAlias, TypeVar

from numpydantic import NDArray, Shape

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
