"""Types for static typing of mappings."""

from collections.abc import Mapping, MutableMapping
from typing import Any, TypeAlias, TypeVar

K = TypeVar("K")
T = TypeVar("T")

Leaf: TypeAlias = Any
"""Leaf node."""
Node: TypeAlias = Mapping[Any, "Node | Leaf"]
"""General node."""
MutableNode: TypeAlias = MutableMapping[Any, "MutableNode | Leaf"]
"""Mutable general node."""
