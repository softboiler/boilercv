"""Morphs."""

from __future__ import annotations

from collections import UserDict, defaultdict
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Any, ClassVar, Generic, Self, TypeVar, overload

from tomlkit import parse
from tomlkit.container import Container
from tomlkit.items import Item

from boilercv.morphs import BaseMorph, M, Morph
from boilercv_pipeline import mappings
from boilercv_pipeline.types import Context, K, Leaf, Model, Node, Pipes, T, V
from boilercv_pipeline.types.runtime import CV, SK, ContextValue, Symbol

# * MARK: Context value handlers


def get_context(
    morphs: Mapping[type, Pipes], context_values: Iterable[ContextValue] | None = None
) -> Context:
    """Get a Pydantic context from morphs and other context values."""
    return Context(compose_context(Morphs(morphs), *(context_values or ())))


def compose_context(*context_values: ContextValue):
    """Compose inner contexts."""
    return {
        context_value.name_to_snake(): context_value for context_value in context_values
    }


class LocalSymbols(UserDict[SK, Symbol], ContextValue, Generic[SK]):
    """Local symbols."""


@dataclass
class Defaults(ContextValue, Generic[K, V]):
    """Context for expression validation."""

    keys: tuple[K, ...] = field(default_factory=tuple)
    """Default keys."""
    value: V | None = None
    """Default value."""
    factory: Callable[..., Any] | None = None
    """Default value factory."""


# * MARK: Hybrid context value and context morph handlers


@dataclass
class Pipe(Generic[T]):
    """Pipe."""

    f: Callable[[T, Any], T]
    context_value: ContextValue


class Morphs(UserDict[type, Pipes], ContextValue):
    """Morphs."""

    def __or__(self, other: Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Morphs):
            merged: dict[type, Pipes] = defaultdict(list)
            for model, pipes in chain.from_iterable([self.items(), other.items()]):
                merged[model].extend(pipes)
            return type(self)(merged)
        if isinstance(other, Mapping):
            return self | type(self)(other)
        return NotImplemented

    def __ror__(self, other):  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Morphs):
            return other | self
        if isinstance(other, Mapping):
            return type(self)(other) | self
        return NotImplemented

    def __ior__(self, other):  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Morphs):
            self.data = (self | other).data
        return self


# * MARK: Context morphs


class ContextMorph(Morph[K, V], Generic[K, V]):
    """Context morph."""

    context: ClassVar[Context] = Context()
    """Context."""

    def model_post_init(self, context: Context | None = None) -> None:
        """Morph the model after initialization."""
        try:
            morphs = self.get_context_value(Morphs, context or self.context)
        except ValueError:
            morphs = Morphs()
        with self.thaw_self(validate=True):
            result = self
            for model, pipes in morphs.items():
                if not isinstance(result, model):
                    model_k, model_v = model.get_inner_types()
                    if not isinstance(model_k, TypeVar) and not isinstance(
                        model_v, TypeVar
                    ):
                        continue
                    self_k, self_v = self.get_inner_types()
                    if isinstance(model_k, TypeVar):
                        model_k = self.validate_hint(self_k, model_k, result.keys())
                    if model_k is not self_k:
                        continue
                    if isinstance(model_v, TypeVar):
                        model_v = self.validate_hint(self_v, model_v, result.values())
                    if model_v is not self_v:
                        continue
                for pipe in pipes:
                    result = (
                        result.pipe(pipe.f, pipe.context_value)
                        if isinstance(pipe, Pipe)
                        else result.pipe(pipe)
                    )
            self.root = result

    @classmethod
    def get_context_value(cls, typ: type[CV], context: Context | None) -> CV:
        """Get context values for a type."""
        key = typ.name_to_snake()
        val = (context or cls.context).get(key)
        if val is None:
            raise ValueError(
                f"Expected context for '{cls}' in model context at '{key}'."
            )
        return val  # pyright: ignore[reportReturnType]

    @classmethod
    def get_pipes(cls, *args, **kwds) -> Pipes:
        """Get pipes for a model."""
        return cls.get_morphs(*args, **kwds)[cls]

    @classmethod
    def get_morphs(cls, *args, **kwds) -> Morphs:
        """Get morphs for a model."""
        return cls.get_context_value(
            typ=Morphs,
            context=cls.get_context(*args, **kwds),  # pyright: ignore[reportAttributeAccessIssue]
        )

    @classmethod
    def model_validate(
        cls: type[Model],
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Context | None = None,
    ) -> Model:
        """Validate a pydantic model instance.

        Args:
            obj: The object to validate.
            strict: Whether to enforce types strictly.
            from_attributes: Whether to extract data from object attributes.
            context: Additional context to pass to the validator.

        Raises
        ------
            ValidationError: If the object could not be validated.

        Returns
        -------
            The validated model instance.
        """
        return super().model_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=(context or cls.context),  # pyright: ignore[reportAttributeAccessIssue]
        )

    @classmethod
    def model_validate_json(
        cls: type[Model],
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: Context | None = None,
    ) -> Model:
        """Usage docs: https://docs.pydantic.dev/2.7/concepts/json/#json-parsing.

        Validate the given JSON data against the Pydantic model.

        Args:
            json_data: The JSON data to validate.
            strict: Whether to enforce types strictly.
            context: Extra variables to pass to the validator.

        Returns
        -------
            The validated Pydantic model.

        Raises
        ------
            ValueError: If `json_data` is not a JSON string.
        """
        return super().model_validate(
            json_data,
            strict=strict,
            context=(context or cls.context),  # pyright: ignore[reportAttributeAccessIssue]
        )


# * MARK: Context morph handlers


def set_defaults(i: ContextMorph[K, V], defaults: Defaults[K, V]) -> ContextMorph[K, V]:
    """Set `self.default_keys` using `self.default_factory` or `self.default`."""
    if not defaults.keys:
        return i
    if any(key not in i for key in defaults.keys):
        if defaults.factory:
            default = defaults.factory()
        elif defaults.value is not None:
            default = defaults.value
        else:
            default = i.get_inner_types()[1]()
        return dict.fromkeys(defaults.keys, default) | i
    return i


# TODO: Consider removing this


class TomlMorph(BaseMorph[M], Generic[M]):
    """Morphable mapping."""

    path: Path
    root: M

    def model_dump(self, *args, **kwds):
        """Dump {attr}`root` instead of {class}`TomlMorph` itself."""
        return self.root.model_dump(*args, **kwds)

    def model_dump_json(self, *args, **kwds):
        """Dump {attr}`root` instead of {class}`TomlMorph` itself."""
        return self.root.model_dump_json(*args, **kwds)

    # ! Root case
    @overload
    def sync(self, src: None = None, dst: None = None) -> Container: ...
    # ! General case
    @overload
    def sync(self, src: Node | Leaf, dst: Item | Container) -> None: ...
    # ! Union
    def sync(
        self, src: Node | Leaf | None = None, dst: Item | Container | None = None
    ) -> Container | None:
        """Sync a TOML document."""
        if not src:
            model_dump: Node = self.model_dump(mode="json")
            src = model_dump
        dst = dst or parse(self.path.read_text("utf-8"))
        return mappings.sync(src, dst)

    def write(self) -> None:
        """Write to TOML."""
        self.path.write_text(self.sync().as_string(), "utf-8")

    @classmethod
    def read(cls, path: Path) -> Self:
        """Read from TOML."""
        return cls(path=path, root=parse(path.read_text("utf-8")))  # type: ignore[reportArgumentType]
