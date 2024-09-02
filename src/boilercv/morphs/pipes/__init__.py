"""Pipes."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic.alias_generators import to_snake


class ContextValue:
    """Context value."""

    @classmethod
    def name_to_snake(cls) -> str:
        """Get name."""
        return to_snake(cls.__name__)


@dataclass
class Pipe:
    """Pipe."""

    f: Callable[[Any, Any], Any]
    context_value: ContextValue


@dataclass
class PipeWithInfo:
    """Pipe with validation info."""

    f: Callable[[Any, Any, Any], Any]
    context_value: ContextValue
