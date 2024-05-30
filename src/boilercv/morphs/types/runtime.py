"""Type annotations used at runtime in {mod}`boilercv_pipeline`."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, Self, TypeAlias, TypeVar

from pydantic.alias_generators import to_snake

from boilercv.morphs.types import S

if TYPE_CHECKING:
    from boilercv.morphs.contexts import Context, Pipe


K = TypeVar("K")
CV = TypeVar("CV", bound="ContextValue", contravariant=True)

SK = TypeVar("SK")
"""Symbol key."""

# ? Pipelines
# ? Making these runtime-checkable doesn't actually check the callable shape


class StaticPipe(Protocol[S]):  # noqa: D101
    def __call__(self, i: S, /) -> S: ...  # noqa: D102


class ContextPipe(Protocol[S]):  # noqa: D101
    def __call__(self, i: S, context: Context, /) -> S: ...  # noqa: D102


AnyPipe: TypeAlias = "Pipe[Any]" | ContextPipe[Any] | StaticPipe[Any]
Pipeline: TypeAlias = tuple[AnyPipe, ...]


class ContextValue:
    """Context value."""

    @classmethod
    def name_to_snake(cls) -> str:
        """Get name."""
        return to_snake(cls.__name__)


@dataclass
class Pipelines:
    """Pipelines."""

    before: Pipeline = field(default_factory=Pipeline)
    after: Pipeline = field(default_factory=Pipeline)

    @classmethod
    def make(
        cls,
        before: Sequence[AnyPipe] | AnyPipe | None = None,
        after: Sequence[AnyPipe] | AnyPipe | None = None,
    ) -> Self:
        """Get validators."""
        before = () if before is None else before
        after = () if after is None else after
        bef = tuple(before) if isinstance(before, Sequence) else (before,)
        aft = tuple(after) if isinstance(after, Sequence) else (after,)
        return cls(before=bef, after=aft)
