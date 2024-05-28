"""Morph."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from types import GenericAlias
from typing import (
    Any,
    Generic,
    Literal,
    Self,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)
from warnings import warn

from pydantic import BaseModel, Field, RootModel, ValidationError

from boilercv.morphs.morph_common import MorphCommon
from boilercv.morphs.types import (
    RK,
    RV,
    DictDict,
    DictType,
    K,
    M,
    MapMap,
    MapType,
    P,
    R,
    TypeDict,
    TypeMap,
    Types,
    TypeType,
    V,
)

TRUNC = 200
"""Truncate representations beyond this length."""


class Morph(RootModel[MutableMapping[K, V]], MorphCommon[K, V], Generic[K, V]):
    """Type-checked, generic, morphable mapping."""

    root: MutableMapping[K, V] = Field(default_factory=dict)
    """Type-checked dictionary as the root data."""

    @classmethod
    def fromkeys(cls, iterable, value=None):  # noqa: D102
        return cls(dict.fromkeys(iterable, value))

    def __repr__(self):
        root = str(self.root)
        return (
            f"{type(self).__name__}(" + root[:TRUNC] + "...)"
            if len(root) > TRUNC
            else f"{type(self).__name__}({self.root})"
        )

    def __iter__(self):  # pyright: ignore[reportIncompatibleMethodOverride]  # Iterate over `root` instead of `self`.
        """Iterate over root mapping."""
        return iter(self.root)

    @classmethod
    def get_inner_types(cls) -> Types:
        """Get types of the keys and values."""
        return Types(*get_args(cls.model_fields["root"].annotation))  # pyright: ignore[reportAttributeAccessIssue]

    # ! (([K, V] -> [K, V]) -> Self)
    @overload
    def pipe(
        self, f: MapMap[K, V, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    @overload
    def pipe(
        self, f: DictDict[K, V, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! ((Self -> [K, V]) -> Self)
    @overload
    def pipe(
        self, f: TypeMap[Self, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    @overload
    def pipe(
        self, f: TypeDict[Self, K, V, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! ((Self -> [RK, RV]) -> Morph[RK, RV])
    @overload
    def pipe(
        self, f: TypeMap[Self, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...
    @overload
    def pipe(
        self, f: TypeDict[Self, RK, RV, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, RV]: ...
    # ! (([K, V] -> R) -> R)
    @overload
    def pipe(self, f: MapType[K, V, R, P], /, *args: P.args, **kwds: P.kwargs) -> R: ...
    @overload
    def pipe(
        self, f: DictType[K, V, R, P], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...
    # ! ((Self -> Self) -> Self)
    @overload
    def pipe(
        self, f: TypeType[Self, Self, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! ((Self -> R) -> R)
    @overload
    def pipe(
        self, f: TypeType[Self, R, P], /, *args: P.args, **kwds: P.kwargs
    ) -> R: ...
    # ! ((Any -> Any) -> Any)
    def pipe(
        self, f: TypeType[Any, Any, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self | Morph[Any, Any] | Any:
        """Pipe."""
        self_k, self_v = self.get_inner_types()
        ret_k = ret_v = None
        if (
            len(hints := get_type_hints(f)) > 1
            and (first_hint := next(iter(get_type_hints(f).values())))
            and (in_hint := self.get_hint(first_hint))
        ):
            in_k, in_v = in_hint
            if ret_hint := self.get_hint(hints.get("return")):
                ret_k, ret_v = ret_hint
                if isinstance(ret_k, TypeVar) and ret_k is in_k:
                    ret_k = self_k
                if isinstance(ret_v, TypeVar) and ret_v is in_v:
                    ret_v = self_v
        return_alike = ret_k is self_k and ret_v is self_v
        with self.thaw(validate=return_alike) as copy:
            try:
                result = f(copy, *args, **kwds)
            except TypeError as err:
                raise TypeError(f"Failed to pipe {type(self)} through {f}.") from err
        if not isinstance(result, Mapping) or not result:
            return result
        if return_alike:
            return self.validate_nearest(result, ret_k, ret_v)
        if all(ret and not isinstance(ret, TypeVar) for ret in (ret_k, ret_v)):
            return self.validate_nearest(result, ret_k, ret_v)
        return self.validate_nearest(
            result,
            self.validate_hint(self_k, ret_k, result.keys()),
            self.validate_hint(self_v, ret_v, result.values()),
        )

    def validate_nearest(
        self, result: Self | Mapping[Any, Any], k: type | None, v: type | None
    ) -> Self | Mapping[Any, Any]:
        """Try validating against own, registered, or parent models, or just return."""
        if k and v and Types(k, v) == self.get_inner_types():
            try:
                return self.model_validate(result)
            except ValidationError:
                pass
        for morph in self.registered_morphs:
            meta = morph.__pydantic_generic_metadata__
            concrete = not meta["origin"]
            ret_k, ret_v = k, v
            if not concrete:
                morph_k, morph_v = meta["args"]
                ret_k = k if isinstance(morph_k, TypeVar) else morph_k
                ret_v = v if isinstance(morph_v, TypeVar) else morph_v
            try:
                return (
                    morph.model_validate(result)
                    if concrete
                    else morph[ret_k, ret_v].model_validate(result)
                )
            except ValidationError:
                pass
        base = previous_base = self
        while (get_parent := getattr(base, "get_parent", None)) and (
            (base := get_parent()) is not previous_base
        ):
            try:
                return base[k, v](result)
            except ValidationError:
                previous_base = base
                continue
        return result

    def get_hint(self, hint: Any) -> Types | None:
        """Get hint."""
        hints = get_args(hint)
        if not hints:
            return None
        if len(hints) == 2:
            return Types(*hints)
        if not isinstance(hint, GenericAlias):
            if issubclass(hint, Morph):
                return hint.get_inner_types()
            if not issubclass(hint, Mapping):
                warn(
                    f"Function to pipe {type(self)} through has input {hint} that doesn't appear to take a mapping.",
                    stacklevel=2,
                )
        return None

    def validate_hint(
        self, self_hint: type, ret_hint: type | TypeVar | None, result: Iterable[Any]
    ) -> type | Any:
        """Validate hint."""
        if not ret_hint or isinstance(ret_hint, TypeVar):
            if (  # noqa: SIM114
                get_origin(self_hint) == Literal
                and (choices := get_args(self_hint))
                and all(k in choices for k in result)
            ):
                return self_hint
            elif all(isinstance(k, self_hint) for k in result):
                return self_hint
        return Any


class BaseMorph(BaseModel, MorphCommon[Any, Any], Generic[M]):
    """Base model with a morph property."""

    root: M
    """Morphable mapping."""

    def __repr__(self):
        root = str(self.root.root)
        return (
            f"{type(self).__name__}(" + root[:TRUNC] + "...)"
            if len(root) > TRUNC
            else f"{type(self).__name__}({self.root})"
        )

    def __iter__(self):  # pyright: ignore[reportIncompatibleMethodOverride]  # Iterate over `root` instead of `self`.
        """Iterate over root mapping."""
        return iter(self.root)

    @classmethod
    def get_inner_types(cls):
        """Get types of the keys and values."""
        return cls.model_fields["root"].annotation.get_inner_types()  # pyright: ignore[reportOptionalMemberAccess]

    def pipe(
        self, f: TypeType[Any, Any, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self:
        """Pipe."""
        with self.thaw() as copy:
            copy.root = self.root.pipe(f, *args, **kwds)
        return copy

    @contextmanager
    def thaw(self, validate: bool = True) -> Iterator[Self]:
        """Produce a thawed copy of an instance."""
        with super().thaw(validate) as base_copy, self.root.thaw(validate) as root_copy:
            base_copy.root = root_copy
            yield base_copy
