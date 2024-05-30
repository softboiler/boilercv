"""Common morph models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping, MutableMapping
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Self, overload

from pydantic import BaseModel, ConfigDict, RootModel

from boilercv.morphs.types import RK, RV, K, P, Types, TypeType, V

if TYPE_CHECKING:
    from boilercv.morphs.morphs import Morph


class MorphCommon(MutableMapping[K, V], ABC, Generic[K, V]):
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

    def __init_subclass__(cls, /, foo: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        parent = cls.get_parent()
        if (
            parent in {BaseModel, RootModel, MorphCommon}
            or cls in parent.registered_morphs
        ):
            return
        parent.register(cls)

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
