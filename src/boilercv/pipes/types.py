"""Types."""

from collections.abc import Callable
from typing import Any, TypeAlias, TypeVar

from boilercv.pipes import ContextValue, Pipe, PipeWithInfo

AnyPipe: TypeAlias = Pipe | PipeWithInfo | Callable[[Any], Any]
"""Any pipe."""
CV = TypeVar("CV", bound=ContextValue, contravariant=True)
"""Context value type."""
