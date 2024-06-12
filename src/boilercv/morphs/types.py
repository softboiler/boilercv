"""Types used in {mod}`~boilercv.morphs`."""

from collections.abc import Callable, MutableMapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NamedTuple,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
    _LiteralGenericAlias,  # pyright: ignore[reportAttributeAccessIssue]
    _UnionGenericAlias,  # pyright: ignore[reportAttributeAccessIssue]
    runtime_checkable,
)

from pydantic import BaseModel

if TYPE_CHECKING:
    from boilercv.morphs.contexts import (
        ContextValue,
        Pipe,
        PipelineContext,
        PipeWithInfo,
    )

AnyPipe: TypeAlias = "Pipe | PipeWithInfo | Callable[[Any], Any]"
"""Any pipe."""
Mode: TypeAlias = Literal["before", "after"]
"""Mode."""
UnionGenericAlias: TypeAlias = _UnionGenericAlias
"""Union type."""
LiteralGenericAlias: TypeAlias = _LiteralGenericAlias
"""Literal type."""
ContextValueLike: TypeAlias = "PipelineContext | ContextValue"
"""Allowable context-value-like values."""

T = TypeVar("T")
"""Type."""
P = TypeVar("P", contravariant=True)
"""Contravariant type to represent parameters."""
R = TypeVar("R", covariant=True)
"""Covariant type to represent returns."""
Ps = ParamSpec("Ps")
"""Parameter type specification."""
K = TypeVar("K")
"""Key type."""
V = TypeVar("V")
"""Value type."""
RK = TypeVar("RK")
"""Return key type that may differ from parameter key type."""
RV = TypeVar("RV")
"""Return value type that may differ from parameter value type."""
CV = TypeVar("CV", bound="ContextValue", contravariant=True)
"""Context value type."""
Model = TypeVar("Model", bound=BaseModel)
"""Model type."""
TypeOfModel = TypeVar("TypeOfModel", bound=type[BaseModel])
"""Type of model type."""


class TypeType(Protocol[P, R, Ps]):  # noqa: D101
    def __call__(self, i: P, /, *args: Ps.args, **kwds: Ps.kwargs) -> R: ...  # noqa: D102


class TypeMap(Protocol[P, K, V, Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: P, /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> MutableMapping[K, V]: ...


class TypeDict(Protocol[P, K, V, Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: P, /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> dict[K, V]: ...


class MapType(Protocol[K, V, R, Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> R: ...


class DictType(Protocol[K, V, R, Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: dict[K, V], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> R: ...


class MapMap(Protocol[K, V, RK, RV, Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> MutableMapping[RK, RV]: ...


class DictDict(Protocol[K, V, RK, RV, Ps]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: dict[K, V], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> dict[RK, RV]: ...


class Types(NamedTuple):
    """Mapping types."""

    key: type
    value: type


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
