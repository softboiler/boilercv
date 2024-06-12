"""Types for static typing of mappings."""

from collections.abc import Mapping, MutableMapping
from typing import Any, TypeAlias, TypeVar

Leaf: TypeAlias = Any
"""Leaf node."""
Node: TypeAlias = Mapping[Any, "Node | Leaf"]
"""General node."""
MutableNode: TypeAlias = MutableMapping[Any, "MutableNode | Leaf"]
"""Mutable general node."""

T = TypeVar("T")
"""Type."""
K = TypeVar("K")
"""Key type."""
V = TypeVar("V")
"""Value type."""
SK = TypeVar("SK", bound=str)
"""String key type."""
MN = TypeVar("MN", bound=MutableNode)
"""Mutable node type."""
