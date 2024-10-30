"""Types."""

from typing import TypeAlias

from numpydantic import NDArray, Shape

VectorShape: TypeAlias = Shape["*"]  # noqa: F722  # pyright: ignore[reportInvalidTypeArguments]
"""Vector shape."""
IntVec: TypeAlias = NDArray[VectorShape, int]  # pyright: ignore[reportInvalidTypeArguments]
"""Integer vector."""
FloatVec: TypeAlias = NDArray[VectorShape, float]  # pyright: ignore[reportInvalidTypeArguments]
"""Float vector."""
