"""Morph."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import suppress
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
    HasModelDump,
    K,
    MapMap,
    MapType,
    Ps,
    R,
    TypeDict,
    TypeMap,
    Types,
    TypeType,
    V,
)

TRUNC = 200
"""Truncate representations beyond this length."""


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
    def morph_cpipe(
        self,
        f: MapMap[K, V, K, V, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    @overload
    def morph_cpipe(
        self,
        f: DictDict[K, V, K, V, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! ((Self -> [K, V]) -> Self)
    @overload
    def morph_cpipe(
        self,
        f: TypeMap[Self, K, V, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    @overload
    def morph_cpipe(
        self,
        f: TypeDict[Self, K, V, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! ((Self -> [RK, RV]) -> Morph[RK, RV])
    @overload
    def morph_cpipe(
        self,
        f: TypeMap[Self, RK, RV, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Morph[RK, RV]: ...
    @overload
    def morph_cpipe(
        self,
        f: TypeDict[Self, RK, RV, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Morph[RK, RV]: ...
    # ! (([K, V] -> R) -> R)
    @overload
    def morph_cpipe(
        self,
        f: MapType[K, V, R, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> R: ...
    @overload
    def morph_cpipe(
        self,
        f: DictType[K, V, R, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> R: ...
    # ! ((Self -> Self) -> Self)
    @overload
    def morph_cpipe(
        self,
        f: TypeType[Self, Self, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! ((Self -> R) -> R)
    @overload
    def morph_cpipe(
        self,
        f: TypeType[Self, R, Ps],
        morph_context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> R: ...
    # ! ((Any -> Any) -> Any)
    def morph_cpipe(
        self,
        f: TypeType[Any, Any, Ps],
        context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self | Morph[Any, Any] | Any:
        """Pipe with context."""
        context = dict(context)
        self_k, self_v = self.morph_get_inner_types()
        out_k, out_v = (Any, Any)
        if (type_hints := get_type_hints(f)) and (hint := type_hints.get("return")):
            hints = get_args(hint)
            if hints and len(hints) == 2:
                out_k, out_v = Types(*hints)
            with suppress(TypeError):
                if issubclass(hint, Morph):
                    out_k, out_v = hint.morph_get_inner_types()
        copy = self.model_validate(obj=self.model_dump(), context=context)
        result = f(copy, *args, **kwds)
        result = (
            result.model_dump(warnings="none")
            if isinstance(result, HasModelDump)
            else result
        )
        if not isinstance(result, Mapping) or not result:
            return result
        result = dict(result)
        k = get_morph_hint(self_k, out_k) or Any
        v = get_morph_hint(self_v, out_v) or Any
        if Types(k, v) == self.morph_get_inner_types():
            return self.model_validate(obj=result, context=context)
        with suppress(ValidationError, TypeError, ValueError):
            return Morph[k, v].model_validate(obj=result, context=context)
        return result

    # ! (([K] -> [K]) -> Self)
    @overload
    def morph_ckpipe(
        self,
        f: TypeType[list[K], list[K], Ps],
        context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! (([K] -> [RK]) -> Morph[RK, V])
    @overload
    def morph_ckpipe(
        self,
        f: TypeType[list[K], list[RK], Ps],
        context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Morph[RK, V]: ...
    # ! (([K] -> [Any]) -> Self | Morph[Any, V]
    def morph_ckpipe(
        self,
        f: TypeType[list[K], list[Any], Ps],
        context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self | Morph[Any, V]:
        """Pipe, morphing keys."""

        def pipe(_, *args: Ps.args, **kwds: Ps.kwargs):
            return dict(
                zip(f(list(self.keys()), *args, **kwds), self.values(), strict=False)
            )

        return self.morph_cpipe(pipe, context, *args, **kwds)

    # ! (([V] -> [V]) -> Self)
    @overload
    def morph_cvpipe(
        self,
        f: TypeType[list[V], list[V], Ps],
        context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! (([V] -> [RV]) -> Morph[K, RV])
    @overload
    def morph_cvpipe(
        self,
        f: TypeType[list[V], list[RV], Ps],
        context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Morph[K, RV]: ...
    # ! (([V] -> [Any]) -> Self | Morph[K, Any]
    def morph_cvpipe(
        self,
        f: TypeType[list[V], list[Any], Ps],
        context: Mapping[str, Any],
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self | Morph[K, Any]:
        """Pipe, morphing values."""

        def pipe(_, *args: Ps.args, **kwds: Ps.kwargs):
            return dict(
                zip(self.keys(), f(list(self.values()), *args, **kwds), strict=False)
            )

        return self.morph_cpipe(pipe, context, *args, **kwds)

    # ! (([K, V] -> [K, V]) -> Self)
    @overload
    def morph_pipe(
        self, f: MapMap[K, V, K, V, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self: ...
    @overload
    def morph_pipe(
        self, f: DictDict[K, V, K, V, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self: ...
    # ! ((Self -> [K, V]) -> Self)
    @overload
    def morph_pipe(
        self, f: TypeMap[Self, K, V, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self: ...
    @overload
    def morph_pipe(
        self, f: TypeDict[Self, K, V, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self: ...
    # ! ((Self -> [RK, RV]) -> Morph[RK, RV])
    @overload
    def morph_pipe(
        self, f: TypeMap[Self, RK, RV, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Morph[RK, RV]: ...
    @overload
    def morph_pipe(
        self, f: TypeDict[Self, RK, RV, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Morph[RK, RV]: ...
    # ! (([K, V] -> R) -> R)
    @overload
    def morph_pipe(
        self, f: MapType[K, V, R, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> R: ...
    @overload
    def morph_pipe(
        self, f: DictType[K, V, R, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> R: ...
    # ! ((Self -> Self) -> Self)
    @overload
    def morph_pipe(
        self, f: TypeType[Self, Self, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self: ...
    # ! ((Self -> R) -> R)
    @overload
    def morph_pipe(
        self, f: TypeType[Self, R, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> R: ...
    # ! ((Any -> Any) -> Any)
    def morph_pipe(
        self, f: TypeType[Any, Any, Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self | Morph[Any, Any] | Any:
        """Pipe."""
        return self.morph_cpipe(f, {}, *args, **kwds)

    # ! (([K] -> [K]) -> Self)
    @overload
    def morph_kpipe(
        self, f: TypeType[list[K], list[K], Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self: ...
    # ! (([K] -> [RK]) -> Morph[RK, V])
    @overload
    def morph_kpipe(
        self, f: TypeType[list[K], list[RK], Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Morph[RK, V]: ...
    # ! (([K] -> [Any]) -> Self | Morph[Any, V]
    def morph_kpipe(
        self, f: TypeType[list[K], list[Any], Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self | Morph[Any, V]:
        """Pipe, morphing keys."""
        return self.morph_ckpipe(f, {}, *args, **kwds)

    # ! (([V] -> [V]) -> Self)
    @overload
    def morph_vpipe(
        self, f: TypeType[list[V], list[V], Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self: ...
    # ! (([V] -> [RV]) -> Morph[K, RV])
    @overload
    def morph_vpipe(
        self, f: TypeType[list[V], list[RV], Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Morph[K, RV]: ...
    # ! (([V] -> [Any]) -> Self | Morph[K, Any]
    def morph_vpipe(
        self, f: TypeType[list[V], list[Any], Ps], /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> Self | Morph[K, Any]:
        """Pipe, morphing values."""
        return self.morph_cvpipe(f, {}, *args, **kwds)

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


def get_morph_hint(
    in_hint: type, out_hint: type | TypeVar | None = None
) -> type | None:
    """Handle missing and {class}`~typing.TypeVar` hints."""
    if in_hint is out_hint:
        return in_hint
    if not out_hint or isinstance(out_hint, TypeVar):
        return in_hint
    return out_hint
