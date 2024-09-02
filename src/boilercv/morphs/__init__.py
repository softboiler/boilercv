"""Morphs."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import suppress
from typing import Any, Generic, Self, TypeVar, get_args, get_type_hints, overload

from pydantic import ValidationError, model_validator

from boilercv.contexts import RootMapping
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


class Morph(RootMapping[K, V], Generic[K, V]):
    """Type-checked, generic, morphable mapping."""

    def __repr__(self):
        root = str(self.root)
        return (
            f"{type(self).__name__}({root[:TRUNC]}...)"
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
    def morph_pipe(
        self,
        f: MapMap[K, V, K, V, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    @overload
    def morph_pipe(
        self,
        f: DictDict[K, V, K, V, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! ((Self -> [K, V]) -> Self)
    @overload
    def morph_pipe(
        self,
        f: TypeMap[Self, K, V, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    @overload
    def morph_pipe(
        self,
        f: TypeDict[Self, K, V, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! ((Self -> [RK, RV]) -> Morph[RK, RV])
    @overload
    def morph_pipe(
        self,
        f: TypeMap[Self, RK, RV, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Morph[RK, RV]: ...
    @overload
    def morph_pipe(
        self,
        f: TypeDict[Self, RK, RV, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Morph[RK, RV]: ...
    # ! (([K, V] -> R) -> R)
    @overload
    def morph_pipe(
        self,
        f: MapType[K, V, R, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> R: ...
    @overload
    def morph_pipe(
        self,
        f: DictType[K, V, R, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> R: ...
    # ! ((Self -> Self) -> Self)
    @overload
    def morph_pipe(
        self,
        f: TypeType[Self, Self, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self: ...
    # ! ((Self -> R) -> R)
    @overload
    def morph_pipe(
        self,
        f: TypeType[Self, R, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> R: ...
    # ! ((Any -> Any) -> Any)
    def morph_pipe(
        self,
        f: TypeType[Any, Any, Ps],
        context: Mapping[str, Any] | None = None,
        /,
        *args: Ps.args,
        **kwds: Ps.kwargs,
    ) -> Self | Morph[Any, Any] | Any:
        """Pipe with context."""
        context = context or {}
        self_k, self_v = self.morph_get_inner_types()
        out_k, out_v = (Any, Any)
        if (type_hints := get_type_hints(f)) and (hint := type_hints.get("return")):
            hints = get_args(hint)
            if hints and len(hints) == 2:
                out_k, out_v = Types(*hints)
            with suppress(TypeError):
                if issubclass(hint, Morph):
                    out_k, out_v = hint.morph_get_inner_types()
        copy = self.model_validate(
            obj=self.model_dump(context=context),  # pyright: ignore[reportArgumentType]
            context=context,
        )
        result = f(copy, *args, **kwds)
        result = (
            result.model_dump(warnings="none", context=context)  # pyright: ignore[reportArgumentType]
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


def get_morph_hint(
    in_hint: type, out_hint: type | TypeVar | None = None
) -> type | None:
    """Handle missing and {class}`~typing.TypeVar` hints."""
    if in_hint is out_hint:
        return in_hint
    return in_hint if not out_hint or isinstance(out_hint, TypeVar) else out_hint
