"""Types for static typing of mappings."""

from collections.abc import Mapping, MutableMapping
from typing import Any, TypeAlias, TypedDict, TypeVar


class AnyTypedDict(TypedDict):
    """Base class representing any typed dictionary."""


Key: TypeAlias = Any
"""Key."""
Leaf: TypeAlias = Any
"""Leaf node."""

MutableNode: TypeAlias = MutableMapping[Key, "MutableNode | Leaf"] | AnyTypedDict
"""Mutable general node."""
MutableNode_T = TypeVar("MutableNode_T", bound=MutableNode)
"""Mutable node type."""

Node: TypeAlias = Mapping[Key, "Node | Leaf"] | AnyTypedDict
"""General node."""
Node_T = TypeVar("Node_T", bound=Node)
"""Node type."""

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
