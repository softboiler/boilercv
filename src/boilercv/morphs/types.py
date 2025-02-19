"""Types used in {mod}`~boilercv.morphs`."""

# TODO: https://github.com/softboiler/boilercv/issues/232
# pyright:reportInvalidTypeVarUse=none

from collections.abc import MutableMapping
from typing import (
    Any,
    Literal,
    NamedTuple,
    ParamSpec,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from pydantic import BaseModel

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

Model = TypeVar("Model", bound=BaseModel)
"""Model type."""
TypeOfModel = TypeVar("TypeOfModel", bound=type[BaseModel])
"""Type of model type."""


class TypeType(Protocol[P, R, Ps]):
    def __call__(self, i: P, /, *args: Ps.args, **kwds: Ps.kwargs) -> R: ...


class TypeMap(Protocol[P, K, V, Ps]):
    def __call__(
        self, i: P, /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> MutableMapping[K, V]: ...


class TypeDict(Protocol[P, K, V, Ps]):
    def __call__(self, i: P, /, *args: Ps.args, **kwds: Ps.kwargs) -> dict[K, V]: ...


class MapType(Protocol[K, V, R, Ps]):
    def __call__(
        self, i: MutableMapping[K, V], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> R: ...


class DictType(Protocol[K, V, R, Ps]):
    def __call__(self, i: dict[K, V], /, *args: Ps.args, **kwds: Ps.kwargs) -> R: ...


class MapMap(Protocol[K, V, RK, RV, Ps]):
    def __call__(
        self, i: MutableMapping[K, V], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> MutableMapping[RK, RV]: ...


class DictDict(Protocol[K, V, RK, RV, Ps]):
    def __call__(
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
