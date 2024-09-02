"""Types."""

from typing import (
    Literal,
    TypeAlias,
    TypeVar,
    _LiteralGenericAlias,  # pyright: ignore[reportAttributeAccessIssue]
    _UnionGenericAlias,  # pyright: ignore[reportAttributeAccessIssue]
)

Mode: TypeAlias = Literal["before", "after"]
"""Mode."""
UnionGenericAlias: TypeAlias = _UnionGenericAlias
"""Union type."""
LiteralGenericAlias: TypeAlias = _LiteralGenericAlias
"""Literal type."""
T = TypeVar("T")
"""Type."""
K = TypeVar("K")
"""Key type."""
V = TypeVar("V")
"""Value type."""
