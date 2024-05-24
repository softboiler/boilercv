"""Morphs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from hashlib import sha512
from types import GenericAlias
from typing import (
    Any,
    ClassVar,
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

from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError

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

TRUNC = 200
"""Truncate representations beyond this length."""


class MorphCommon(MutableMapping[K, V], ABC, Generic[K, V]):  # noqa: PLR0904
    """Abstract base class for morphable mappings.

    Generally, you should subclass from {class}`Morph` or {class}`BaseMorph` for
    {class}`Morph`-like mappings.

    ```
    class MyMorph(RootModel[MutableMapping[K, V]], MorphCommon[K, V], Generic[K, V]):  # noqa: PLR0904
        root: MutableMapping[K, V] = Field(default_factory=dict)
    ```

    ```
    class MyBaseMorph(BaseModel, MorphCommon[K, V], Generic[K, V]):
        root: Morph[K, V] = Field(default_factory=Morph[K, V])
    ```
    """

    model_config: ClassVar = ConfigDict(frozen=True)
    """Root configuration, merged with subclass configs."""
    registered_morphs: ClassVar[tuple[type, ...]] = ()  # type: ignore
    """Pipeline outputs not matching this model will attempt to match these."""

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        """Iterate over root mapping.

        Should implement trivially as `return iter(self.root)` in subclasses inheriting
        from `pydantic.RootModel` or `pydantic.BaseModel`, otherwise `__iter__` is
        hijacked by the `pydantic` metaclass.
        """

    @classmethod
    @abstractmethod
    def get_inner_types(cls) -> Types:
        """Get types of the keys and values."""

    @abstractmethod
    def pipe(
        self, f: TypeType[Any, Any, P], /, *args: P.args, **kwds: P.kwargs
    ) -> Self | Morph[Any, Any] | Any:
        """Pipe."""

    @classmethod
    def register(cls, model: type):
        """Register the model."""
        cls.registered_morphs = (*cls.registered_morphs, model)

    @classmethod
    def get_parent(cls) -> type:
        """Get parent model class."""
        meta = getattr(cls, "__pydantic_generic_metadata__", None)
        if meta and meta["origin"]:
            return meta["origin"]
        if mro := cls.mro():
            return mro[1] if len(mro) > 1 else mro[0]
        return object

    @contextmanager
    def thaw(self, validate: bool = False) -> Iterator[Self]:
        """Produce a thawed copy of an instance."""
        copy = self.model_copy()  # pyright: ignore[reportAttributeAccessIssue]
        orig_config = copy.model_config
        try:
            type(copy).model_config = (
                orig_config
                | ConfigDict(frozen=False)
                | (ConfigDict(validate_assignment=True) if validate else {})
            )
            yield copy
        finally:
            if validate:
                copy.root = copy.root
            type(copy).model_config = orig_config

    @contextmanager
    def thaw_self(self, validate: bool = True) -> Iterator[None]:
        """Produce a thawed copy of an instance."""
        orig_config = self.model_config
        try:
            type(self).model_config = (
                orig_config
                | ConfigDict(frozen=False)
                | (ConfigDict(validate_assignment=True) if validate else {})
            )
            yield
        finally:
            if validate:
                self.root = self.root
            type(self).model_config = orig_config

    def __hash__(self):
        # ? https://github.com/pydantic/pydantic/issues/1303#issuecomment-2052395207
        return int.from_bytes(
            sha512(
                f"{self.__class__.__qualname__}::{self.model_dump_json()}".encode(  # pyright: ignore[reportAttributeAccessIssue]
                    "utf-8", errors="ignore"
                )
            ).digest()
        )

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

    def __len__(self):
        return len(self.root)  # pyright: ignore[reportAttributeAccessIssue]

    def __getitem__(self, key: K) -> V:
        if key in self.root:  # pyright: ignore[reportAttributeAccessIssue]
            return self.root[key]  # pyright: ignore[reportAttributeAccessIssue]
        if missing := getattr(self.__class__, "__missing__", None):
            return missing(self, key)
        raise KeyError(key)

    def __setitem__(self, key: K, item: V):
        self._check_frozen(key, item)  # pyright: ignore[reportAttributeAccessIssue]
        self.root[key] = item  # pyright: ignore[reportAttributeAccessIssue]

    def __delitem__(self, key: K):
        self._check_frozen(key, None)  # pyright: ignore[reportAttributeAccessIssue]
        del self.root[key]  # pyright: ignore[reportAttributeAccessIssue]

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key: K):  # pyright: ignore[reportIncompatibleMethodOverride]
        return key in self.root  # pyright: ignore[reportAttributeAccessIssue]

    def __or__(self, other) -> Self:
        if isinstance(other, Mapping):
            return self.model_validate(self | dict(other))  # pyright: ignore[reportAttributeAccessIssue]
        return NotImplemented

    def __ror__(self, other) -> Self:
        if isinstance(other, Mapping):
            return self.model_validate(dict(other) | dict(self))  # pyright: ignore[reportAttributeAccessIssue]
        return NotImplemented

    def __ior__(self, other) -> Self:
        return self | other


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
        if return_alike or not isinstance(result, Mapping) or not result:
            return result
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
        self, self_hint: type, ret_hint: type | None, result: Iterable[Any]
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


M = TypeVar("M", bound=Morph[Any, Any])


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
