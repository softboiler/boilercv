"""Types for static typing of mappings."""

from collections.abc import Mapping, MutableMapping
from typing import Any, TypeAlias, TypeVar

MutableNode: TypeAlias = MutableMapping[Any, "MutableNode | Leaf"]
"""Mutable general node."""

K = TypeVar("K")
V = TypeVar("V")
SK = TypeVar("SK", bound=str)
T = TypeVar("T")
MN = TypeVar("MN", bound=MutableNode)

Leaf: TypeAlias = Any
"""Leaf node."""
Node: TypeAlias = Mapping[Any, "Node | Leaf"]
"""General node."""
