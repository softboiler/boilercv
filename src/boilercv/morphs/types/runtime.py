"""Type annotations used at runtime in {mod}`boilercv_pipeline`."""

from __future__ import annotations

from typing import TypeVar

from pydantic.alias_generators import to_snake

K = TypeVar("K")
CV = TypeVar("CV", bound="ContextValue", contravariant=True)

SK = TypeVar("SK")
"""Symbol key."""


class ContextValue:
    """Context value."""

    @classmethod
    def name_to_snake(cls) -> str:
        """Get name."""
        return to_snake(cls.__name__)
