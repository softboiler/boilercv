"""Types."""

from collections.abc import Iterable, Mapping
from typing import Any, TypeAlias

Attributes: TypeAlias = Iterable[str]
FixtureStore: TypeAlias = dict[str, Any]
Params: TypeAlias = Mapping[str, Any]
