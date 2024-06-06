"""Type annotations used at runtime in {mod}`boilercv_pipeline`."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Protocol,
    Self,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

from pydantic.alias_generators import to_snake

if TYPE_CHECKING:
    from boilercv.morphs.contexts import Pipe, PipeWithInfo

# ? Pipelines
# ? Making these runtime-checkable doesn't actually check the callable shape


class ContextValue:
    """Context value."""

    @classmethod
    def name_to_snake(cls) -> str:
        """Get name."""
        return to_snake(cls.__name__)


CV = TypeVar("CV", bound=ContextValue, contravariant=True)
AnyPipe: TypeAlias = "Pipe | PipeWithInfo | Callable[[Any], Any]"


@dataclass
class Pipelines:
    """Pipelines."""

    before: tuple[AnyPipe, ...] = field(default_factory=tuple)
    after: tuple[AnyPipe, ...] = field(default_factory=tuple)

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


@runtime_checkable
class HasModelDump(Protocol):
    """Has model dump."""

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",  # noqa: PYI051
        include: Any = None,
        exclude: Any = None,
        context: dict[str, Any] | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> Any:
        """Model dump."""
