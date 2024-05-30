"""Static type annotations used in {mod}`morphs`."""

from collections.abc import MutableMapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NamedTuple,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypeVar,
)

from pydantic import BaseModel

if TYPE_CHECKING:
    from boilercv.morphs.morphs import Morph


M = TypeVar("M", bound="Morph[Any, Any]")

T = TypeVar("T", contravariant=True)
R = TypeVar("R", covariant=True)
P = ParamSpec("P")


class TypeType(Protocol[T, R, P]):  # noqa: D101
    def __call__(self, i: T, /, *args: P.args, **kwds: P.kwargs) -> R: ...  # noqa: D102


K = TypeVar("K")
V = TypeVar("V")


class TypeMap(Protocol[T, K, V, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: T, /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[K, V]: ...


class TypeDict(Protocol[T, K, V, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: T, /, *args: P.args, **kwds: P.kwargs
    ) -> dict[K, V]: ...


class MapType(Protocol[K, V, R, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...


class DictType(Protocol[K, V, R, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: dict[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...


RK = TypeVar("RK")
RV = TypeVar("RV")


class MapMap(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: MutableMapping[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> MutableMapping[RK, RV]: ...


class DictDict(Protocol[K, V, RK, RV, P]):  # noqa: D101
    def __call__(  # noqa: D102
        self, i: dict[K, V], /, *args: P.args, **kwds: P.kwargs
    ) -> dict[RK, RV]: ...


KT = TypeVar("KT", bound=type)
VT = TypeVar("VT", bound=type)


class Types(NamedTuple):
    """Inner types for mapings."""

    key: type
    value: type


S = TypeVar("S")
Model = TypeVar("Model", bound=BaseModel)

Mode: TypeAlias = Literal["before", "after"]
"""Mode."""
