"""Morph."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from types import GenericAlias
from typing import (
    Any,
    ClassVar,
    Generic,
    Self,
    TypeVar,
    get_args,
    get_type_hints,
    overload,
)

from pydantic import ConfigDict, Field, RootModel, ValidationError, model_validator

from boilercv.morphs.types import (
    RK,
    RV,
    DictDict,
    DictType,
    K,
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
from boilercv.morphs.types.runtime import HasModelDump

TRUNC = 200
"""Truncate representations beyond this length."""


def get_morph_hint(
    in_hint: type, out_hint: type | TypeVar | None = None
) -> type | None:
    """Handle missing and {attr}`~typing.TypeVar` hints."""
    if in_hint is out_hint:
        return in_hint
    if not out_hint or isinstance(out_hint, TypeVar):
        return in_hint
    return out_hint


class Morph(RootModel[MutableMapping[K, V]], MutableMapping[K, V], Generic[K, V]):  # noqa: PLR0904
    """Type-checked, generic, morphable mapping."""

    root: MutableMapping[K, V] = Field(default_factory=dict)
    """Type-checked dictionary as the root data."""
    model_config: ClassVar = ConfigDict(protected_namespaces=("model_", "morph_"))
    """Root configuration, merged with subclass configs."""

    def __repr__(self):
        root = str(self.root)
        return (
            f"{type(self).__name__}(" + root[:TRUNC] + "...)"
            if len(root) > TRUNC
            else f"{type(self).__name__}({self.root})"
        )

    @classmethod
    def morph_get_inner_types(cls) -> Types:
        """Get types of the keys and values."""
        return Types(*get_args(cls.model_fields["root"].annotation))

    @model_validator(mode="before")
    @classmethod
    def morph_check_parametrized(cls, morph):
        """Qualify."""
        if cls.__pydantic_generic_metadata__["parameters"]:
            raise ValueError("Cannot instantiate generic morphs.")
        return morph

    # ! (([K, V] -> [K, V]) -> Self)
    @overload
    def context_pipe(
        self,
        f: MapMap[K, V, K, V, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Self: ...
    @overload
    def context_pipe(
        self,
        f: DictDict[K, V, K, V, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Self: ...
    # ! ((Self -> [K, V]) -> Self)
    @overload
    def context_pipe(
        self,
        f: TypeMap[Self, K, V, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Self: ...
    @overload
    def context_pipe(
        self,
        f: TypeDict[Self, K, V, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Self: ...
    # ! ((Self -> [RK, RV]) -> Morph[RK, RV])
    @overload
    def context_pipe(
        self,
        f: TypeMap[Self, RK, RV, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Morph[RK, RV]: ...
    @overload
    def context_pipe(
        self,
        f: TypeDict[Self, RK, RV, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Morph[RK, RV]: ...
    # ! (([K, V] -> R) -> R)
    @overload
    def context_pipe(
        self,
        f: MapType[K, V, R, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> R: ...
    @overload
    def context_pipe(
        self,
        f: DictType[K, V, R, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> R: ...
    # ! ((Self -> Self) -> Self)
    @overload
    def context_pipe(
        self,
        f: TypeType[Self, Self, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Self: ...
    # ! ((Self -> R) -> R)
    @overload
    def context_pipe(
        self,
        f: TypeType[Self, R, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> R: ...
    # ! ((Any -> Any) -> Any)
    def context_pipe(
        self,
        f: TypeType[Any, Any, P],
        morph_context: Mapping[str, Any],
        /,
        *args: P.args,
        **kwds: P.kwargs,
    ) -> Self | Morph[Any, Any] | Any:
        """Pipe with context."""
        context = dict(morph_context)
        self_k, self_v = self.morph_get_inner_types()
        out_k, out_v = (Any, Any)
        if (type_hints := get_type_hints(f)) and (hint := type_hints.get("return")):
            hints = get_args(hint)
            if hints and len(hints) == 2:
                out_k, out_v = Types(*hints)
            elif not isinstance(hint, GenericAlias) and issubclass(hint, Morph):
                out_k, out_v = hint.morph_get_inner_types()
        try:
            copy = self.model_validate(obj=self, context=context)
        except (ValidationError, TypeError, ValueError):
            copy = self.model_copy(deep=True)
        result = f(copy, *args, **kwds)
        result = (
            result.model_dump(warnings="none")
            if isinstance(result, HasModelDump)
            else result
        )
        if not isinstance(result, Mapping) or not result:
            return result
        k = get_morph_hint(self_k, out_k) or Any
        v = get_morph_hint(self_v, out_v) or Any
        if Types(k, v) == self.morph_get_inner_types():
            return self.model_validate(obj=dict(result), context=context)
        try:
            return Morph[k, v].model_validate(obj=dict(result), context=context)
        except (ValidationError, TypeError, ValueError):
            pass
        return result

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
        return self.context_pipe(f, {}, *args, **kwds)

    # ! (([K] -> [K]) -> Self)
    @overload
    def pipe_keys(
        self, f: TypeType[list[K], list[K], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! (([K] -> [RK]) -> Morph[RK, V])
    @overload
    def pipe_keys(
        self, f: TypeType[list[K], list[RK], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[RK, V]: ...
    # ! (([K] -> [Any]) -> Self | Morph[Any, V]
    def pipe_keys(
        self, f: TypeType[list[K], list[Any], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self | Morph[Any, V]:
        """Pipe, morphing keys."""

        def pipe(_, *args: P.args, **kwds: P.kwargs):
            return dict(
                zip(f(list(self.keys()), *args, **kwds), self.values(), strict=False)
            )

        return self.pipe(pipe, *args, **kwds)

    # ! (([V] -> [V]) -> Self)
    @overload
    def pipe_values(
        self, f: TypeType[list[V], list[V], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self: ...
    # ! (([V] -> [RV]) -> Morph[K, RV])
    @overload
    def pipe_values(
        self, f: TypeType[list[V], list[RV], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Morph[K, RV]: ...
    # ! (([V] -> [Any]) -> Self | Morph[K, Any]
    def pipe_values(
        self, f: TypeType[list[V], list[Any], P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self | Morph[K, Any]:
        """Pipe, morphing values."""

        def pipe(_, *args: P.args, **kwds: P.kwargs):
            return dict(
                zip(self.keys(), f(list(self.values()), *args, **kwds), strict=False)
            )

        return self.pipe(pipe, *args, **kwds)

    # `MutableMapping` methods adapted from `collections.UserDict`, but with `data`
    # replaced by `root`and `hasattr` guard changed to equivalent `getattr(..., None)`
    # pattern in `__getitem__`. This is done to prevent inheriting directly from
    # `UserDict`, which doesn't play nicely with `pydantic.RootModel`.
    # Source: https://github.com/python/cpython/blob/7d7eec595a47a5cd67ab420164f0059eb8b9aa28/Lib/collections/__init__.py#L1121-L1211

    @classmethod
    def fromkeys(cls, iterable, value=None):  # noqa: D102
        return cls(dict.fromkeys(iterable, value))

    def __len__(self):
        return len(self.root)

    def __getitem__(self, key: K) -> V:
        if key in self.root:
            return self.root[key]
        if missing := getattr(self.__class__, "__missing__", None):
            return missing(self, key)
        raise KeyError(key)

    def __iter__(self) -> Iterator[K]:  # pyright: ignore[reportIncompatibleMethodOverride] iterate over `root` instead of `self`
        return iter(self.root)

    def __setitem__(self, key: K, item: V):
        self.root[key] = item

    def __delitem__(self, key: K):
        del self.root[key]

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key: K):  # pyright: ignore[reportIncompatibleMethodOverride]
        return key in self.root

    def __or__(self, other: HasModelDump | Mapping[Any, Any] | Any) -> Self:
        if isinstance(other, Mapping) and isinstance(other, HasModelDump):
            return self.model_construct(self.model_dump() | other.model_dump())
        if isinstance(other, Mapping):
            return self.model_construct(self.model_dump() | other)
        return NotImplemented

    def __ror__(self, other: HasModelDump | Mapping[Any, Any] | Any) -> Self:
        if isinstance(other, Mapping) and isinstance(other, HasModelDump):
            return self.model_construct(other.model_dump() | self.model_dump())
        if isinstance(other, Mapping):
            return self.model_construct(other | self.model_dump())
        return NotImplemented

    def __ior__(self, other) -> Self:
        return self | other
