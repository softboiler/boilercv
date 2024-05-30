"""Contextual morphs."""

from __future__ import annotations

from abc import ABC
from collections import UserDict, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from inspect import signature
from itertools import chain
from typing import Any, ClassVar, Generic, Self, TypeVar

import sympy
from pydantic import BaseModel, ConfigDict, ValidationInfo, model_validator
from sympy import symbols

from boilercv.morphs.morphs import BaseMorph, Morph
from boilercv.morphs.types import K, Mode, Model, S, V
from boilercv.morphs.types.runtime import CV, AnyPipe, ContextValue, Pipelines

# * MARK: Context value handlers


def compose_contexts(*contexts: Context) -> Context:
    """Compose contexts."""
    context = Context()
    for ctx in contexts:
        context |= ctx
    return context


def compose_context(*context_values: ContextValue) -> Context:
    """Compose inner contexts."""
    return Context({
        context_value.name_to_snake(): context_value for context_value in context_values
    })


def compose_defaults(
    model: type[ContextMorph[Any, Any]],
    mapping: dict[K, V | BaseModel] | None = None,
    keys: tuple[K, ...] | None = None,
    value: V | BaseModel | None = None,
    value_copy_method: Callable[[V | BaseModel], V | BaseModel] = deepcopy,
    factory: Callable[..., Any] | None = None,
    value_model: type[ContextMorph[K, V] | BaseModel] | None = None,
    value_context: Context | None = None,
) -> Context:
    """Compose defaults."""
    context = value_context or Context()
    if value_model is not None:
        context = context or value_model.get_context()  # pyright: ignore[reportAttributeAccessIssue]
        if value is not None:
            raise ValueError("Cannot specify both 'value' and 'model'.")
        value = (
            value_model.context_model_validate(context=context)
            if issubclass(value_model, ContextMorph)
            else value_model.model_validate(obj={}, context=dict(context))
        )
    defaults = (
        Defaults(mapping=mapping, value_copier=value_copy_method)
        if mapping
        else Defaults(
            keys=keys or (),
            value=value,
            factory=factory,
            value_copier=value_copy_method,
        )
    )
    return compose_contexts(
        compose_context(
            Morphs({model: Pipelines.make(before=Pipe(set_defaults, defaults))})
        ),
        context,
    )


def compose_pipelines(
    typ: type,
    /,
    before: Sequence[AnyPipe] | AnyPipe | None = None,
    after: Sequence[AnyPipe] | AnyPipe | None = None,
) -> Context:
    """Compose defaults."""
    return compose_context(Morphs({typ: Pipelines.make(before=before, after=after)}))


class LocalSymbols(UserDict[str, sympy.Symbol], ContextValue):
    """Local symbols."""

    @classmethod
    def from_iterable(cls, syms: Iterable[str]):
        """Create from an iterable of symbols."""
        return cls(
            zip(
                syms,
                symbols(syms, nonnegative=True, real=True, finite=True),
                strict=True,
            )
        )


@dataclass
class Defaults(ContextValue, Generic[K, V]):
    """Context for expression validation."""

    mapping: dict[K, V] = field(default_factory=dict)
    """Mapping of keys to their default values."""
    keys: tuple[K, ...] = field(default_factory=tuple)
    """Default keys."""
    value: V | None = None
    """Default value."""
    factory: Callable[..., Any] | None = None
    """Default value factory."""
    value_copier: Callable[[V], V] | None = deepcopy
    """Method to copy the default value."""


# * MARK: Hybrid context value and context morph handlers


class Context(UserDict[str, ContextValue]):
    """Morphs."""

    def __or__(self, other: Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Context):
            merged = dict(self) | dict(other)
            if (morphs := get_context_value(Morphs, self)) is not None and (
                other_morphs := get_context_value(Morphs, other)
            ) is not None:
                merged[get_context_key(Morphs)] = morphs | other_morphs
            return type(self)(merged)
        if isinstance(other, Mapping):
            return self | type(self)(other)
        return NotImplemented

    def __ror__(self, other):  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Context):
            return other | self
        if isinstance(other, Mapping):
            return type(self)(other) | self
        return NotImplemented

    def __ior__(self, other):  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Context):
            self.data = (self | other).data
        return self


@dataclass
class Pipe(Generic[S]):
    """Pipe."""

    f: Callable[[S, Any], S]
    context_value: ContextValue


class Morphs(UserDict[type, Pipelines], ContextValue):
    """Morphs."""

    def __or__(self, other: Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Morphs):
            merged: dict[type, Pipelines] = defaultdict(Pipelines)
            for model, pipeline in chain.from_iterable([self.items(), other.items()]):
                merged[model].before += pipeline.before
                merged[model].after += pipeline.after
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


# * MARK: Context models


class BaseContext(ContextValue, ABC):
    """Base class for contextualized models."""

    model_config: ClassVar = ConfigDict(
        protected_namespaces=(
            *(BaseMorph.model_config.get("protected_namespaces") or []),
            "context_",
        )
    )

    @model_validator(mode="before")
    @classmethod
    def validate_context_before(
        cls, data: dict[str, Any], info: ValidationInfo, /
    ) -> dict[str, Any]:
        """Validate context."""
        return apply(model=cls, mode="before", data=data, info=info)

    @model_validator(mode="after")
    def validate_context_after(self, info: ValidationInfo, /) -> Self:
        """Validate context."""
        return apply(model=type(self), mode="after", data=self, info=info)

    @classmethod
    def context_model_validate(
        cls: type[Model],  # pyright: ignore[reportGeneralTypeIssues]
        obj: Any | None = None,
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
        return cls.model_validate(  # pyright: ignore[reportAttributeAccessIssue]
            obj or {},
            strict=strict,
            from_attributes=from_attributes,
            context=context or Context(),  # pyright: ignore[reportArgumentType]
        )

    @classmethod
    def context_model_validate_json(
        cls: type[Model],  # pyright: ignore[reportGeneralTypeIssues]
        json_data: str | bytes | bytearray = "{}",
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
        return cls.model_validate(  # pyright: ignore[reportAttributeAccessIssue]
            json_data,
            strict=strict,
            context=context or Context(),  # pyright: ignore[reportArgumentType]
        )


class ContextMorph(Morph[K, V], BaseContext, Generic[K, V]):
    """Context morph."""


class ContextBaseModel(BaseModel, BaseContext):
    """Context base model."""


MSG = "Both model and data are 'ContextMorph' instances with incompatible data."


def apply(  # noqa: C901, PLR0912
    model: type,
    mode: Mode | Any,
    data: S,
    info: ValidationInfo | None = None,
    context: Context | None = None,
) -> S:
    """Apply a pipe to data."""
    info_context = info.context if info else Context()
    ctx = context or info_context or Context()
    morphs = get_context_value(Morphs, ctx) or Morphs()
    pipelines = morphs.get(model)
    if pipelines is None:
        return data
    match mode:
        case "after":
            pipeline = pipelines.after
        case "before":
            pipeline = pipelines.before
        case _:
            raise ValueError("Invalid mode.")
    if not pipeline:
        return data
    if (
        isinstance(model, ContextMorph)
        and isinstance(data, ContextMorph)
        and not isinstance(data, model)
    ):
        model_k, model_v = model.get_inner_types()
        if not isinstance(model_k, TypeVar) and not isinstance(model_v, TypeVar):
            raise ValueError(MSG)  # noqa: TRY004 so Pydantic catches it
        self_k, self_v = data.get_inner_types()
        if isinstance(model_k, TypeVar):
            model_k = data.validate_hint(self_k, model_k, data.keys())
        if model_k is not self_k:
            raise ValueError(MSG)
        if isinstance(model_v, TypeVar):
            model_v = data.validate_hint(self_v, model_v, data.values())
        if model_v is not self_v:
            raise ValueError(MSG)
    for pipe in pipeline:
        if isinstance(pipe, Pipe):
            data = (  # pyright: ignore[reportAssignmentType]
                data.pipe(pipe.f, pipe.context_value)
                if isinstance(data, ContextMorph)
                else pipe.f(data, pipe.context_value)
            )
            continue
        if not isinstance(pipe, Callable):
            raise ValueError("Pipe is not a callable.")  # noqa: TRY004 so Pydantic catches it
        params = signature(pipe).parameters
        if len(params) == 1:
            data = pipe(data)  # pyright: ignore[reportCallIssue]
            continue
        if len(params) == 2:
            data = pipe(data, ctx)  # pyright: ignore[reportCallIssue]
            continue
        raise ValueError("Pipe has too many parameters.")
    return data  # pyright: ignore[reportReturnType]


# * MARK: Context morph handlers


def set_defaults(i: dict[K, V], d: Defaults[K, V]) -> dict[K, V]:
    """Set `self.default_keys` using `self.default_factory` or `self.default`."""
    if not d.value_copier:
        d.value_copier = lambda v: v
    if d.mapping:
        if d.keys or d.value or d.factory:
            raise ValueError(
                "Cannot specify both 'mapping' and 'keys', 'value', or 'factory'."
            )
        return {key: d.value_copier(v) for key, v in d.mapping.items()} | i
    if not d.keys:
        return i
    if any(key not in i for key in d.keys):
        if d.factory:
            return {key: d.factory() for key in d.keys} | i
        if d.value is not None:
            return {key: d.value_copier(d.value) for key in d.keys} | i
        raise ValueError("No default value or factory specified.")
    return i


def get_context_value(value_type: type[CV], context: Context | None) -> CV | None:
    """Get context values for a type."""
    return (context or Context()).get(get_context_key(value_type))  # pyright: ignore[reportReturnType]


def get_context_key(value_type: type[CV]) -> str:
    """Get context keys for a type."""
    return value_type.name_to_snake()
