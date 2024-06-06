"""Contextual morphs."""

from __future__ import annotations

from collections import UserDict, defaultdict
from collections.abc import Callable, Mapping, Sequence
from contextlib import suppress
from copy import deepcopy
from dataclasses import dataclass, field
from itertools import chain
from typing import Any, ClassVar, Generic, Self, get_args

from pydantic import BaseModel, ConfigDict, ValidationInfo, model_validator

from boilercv.morphs.morphs import Morph
from boilercv.morphs.types import K, LiteralKeys, Mode, Model, S, V
from boilercv.morphs.types.runtime import (
    CV,
    AnyPipe,
    ContextValue,
    HasModelDump,
    Pipelines,
)

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


def compose_pipelines(
    typ: type,
    /,
    before: Sequence[AnyPipe] | AnyPipe | None = None,
    after: Sequence[AnyPipe] | AnyPipe | None = None,
) -> Context:
    """Compose defaults."""
    return compose_context(
        PipelinesContext({typ: Pipelines.make(before=before, after=after)})
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


# * MARK: Context value handlers


@dataclass
class Pipe:
    """Pipe."""

    f: Callable[[Any, Any], Any]
    context_value: ContextValue


@dataclass
class PipeWithInfo:
    """Pipe with validation info."""

    f: Callable[[Any, Any, Any], Any]
    context_value: ContextValue


class PipelinesContext(UserDict[Any, Pipelines], ContextValue):
    """Morphs."""

    def __or__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: Self | Mapping[Any, Pipelines] | Any
    ) -> Self:
        if isinstance(other, PipelinesContext):
            merged: dict[Any, Pipelines] = defaultdict(Pipelines)
            for model, pipeline in chain.from_iterable([self.items(), other.items()]):
                merged[model].before += pipeline.before
                merged[model].after += pipeline.after
            return type(self)(merged)
        if isinstance(other, Mapping):
            return self | type(self)(other)
        return NotImplemented

    def __ror__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: Self | Mapping[Any, Pipelines] | Any
    ) -> Self:
        if isinstance(other, Mapping):
            return type(self)(other) | self
        return NotImplemented

    def __ior__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: Self | Mapping[Any, Pipelines] | Any
    ) -> Self:
        self.data = (self | other).data
        return self


class Context(UserDict[str, PipelinesContext | ContextValue]):
    """Morphs."""

    @property
    def pipelines(self) -> PipelinesContext:
        """Get pipelines."""
        context = self.get(get_context_key(PipelinesContext), PipelinesContext())
        return context if isinstance(context, PipelinesContext) else PipelinesContext()

    def __or__(self, other: Context | Mapping[str, Any] | Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Context):
            merged = dict(self) | dict(other)
            if (morphs := get_context_value(PipelinesContext, self)) is not None and (
                other_morphs := get_context_value(PipelinesContext, other)
            ) is not None:
                merged[get_context_key(PipelinesContext)] = morphs | other_morphs
            return type(self)(merged)
        if isinstance(other, Mapping):
            return self | type(self)(other)
        return NotImplemented

    def __ror__(self, other: Context | Mapping[str, Any] | Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Mapping):
            return type(self)(other) | self
        return NotImplemented

    def __ior__(self, other: Context | Mapping[str, Any] | Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        self.data = (self | other).data
        return self


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
        raise ValueError("Must supply either 'mapping' or 'keys'.")
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


# * MARK: Context models


class BaseContext(ContextValue):
    """Base class for contextualized models."""

    model_config: ClassVar = ConfigDict(
        protected_namespaces=(
            *(Morph.model_config.get("protected_namespaces") or []),
            "context_",
        )
    )

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
        obj = obj.model_dump() if isinstance(obj, HasModelDump) else obj
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

    @model_validator(mode="before")
    @classmethod
    def context_validate_before(cls, data: dict[K, V], info: ValidationInfo) -> Self:
        """Validate context before."""
        return cls.apply(mode="before", data=data, info=info)

    @model_validator(mode="after")
    def context_validate_after(self, info: ValidationInfo) -> Self:
        """Validate context after."""
        return self.apply(mode="after", data=self, info=info)

    @classmethod
    def apply(  # noqa: C901
        cls, mode: Mode | Any, data: Self | dict[K, V], info: ValidationInfo
    ) -> Self:
        """Apply a pipe to data."""
        context = Context(info.context) or Context()
        pipelines_context = (
            get_context_value(PipelinesContext, context) or PipelinesContext()
        )
        pipelines = pipelines_context.get(cls)  # pyright: ignore[reportArgumentType]
        result = data if isinstance(data, cls) else cls.model_construct(data)
        if pipelines is None:
            return result
        match mode:
            case "after":
                pipeline = pipelines.after
            case "before":
                pipeline = pipelines.before
            case _:
                raise ValueError("Invalid mode.")
        if not pipeline:
            return result
        if mode == "before":
            for pipe in pipeline:
                if isinstance(pipe, Pipe):
                    result = pipe.f(result, pipe.context_value)
                    continue
                if isinstance(pipe, PipeWithInfo):
                    pipe.f(result, pipe.context_value, info)
                    result = result.context_pipe(
                        pipe.f, context, pipe.context_value, info
                    )
                    continue
                if isinstance(pipe, Callable):
                    result = pipe(result)
                    continue
                raise ValueError("Invalid pipe.")
            return result
        for pipe in pipeline:
            if isinstance(pipe, Pipe):
                result = result.context_pipe(pipe.f, context, pipe.context_value)
                continue
            if isinstance(pipe, PipeWithInfo):
                result = result.context_pipe(pipe.f, context, pipe.context_value, info)
                continue
            if isinstance(pipe, Callable):
                result = result.context_pipe(pipe, context)
                continue
            raise ValueError("Invalid pipe.")
        return result

    @classmethod
    def compose_defaults(
        cls,
        mapping: dict[K, V | BaseModel] | None = None,
        keys: tuple[K, ...] | None = None,
        value: V | BaseModel | None = None,
        value_copy_method: Callable[[V | BaseModel], V | BaseModel] = deepcopy,
        factory: Callable[..., Any] | None = None,
        value_model: type[ContextMorph[K, V] | ContextBaseModel | BaseModel]
        | None = None,
        value_context: Context | None = None,
    ) -> Context:
        """Compose defaults."""
        k, v = cls.morph_get_inner_types()
        if isinstance(k, LiteralKeys):
            keys = keys or get_args(k)
        with suppress(TypeError):
            if issubclass(v, BaseModel):
                value_model = value_model or v
        keys = keys or get_args(cls.morph_get_inner_types().key)
        value_context = value_context or Context()
        if value_model:
            value = (
                value_model.context_model_validate(context=value_context)
                if issubclass(value_model, ContextMorph | ContextBaseModel)
                else value_model.model_validate(obj={}, context=dict(value_context))
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
        context = compose_context(
            PipelinesContext({cls: Pipelines.make(before=Pipe(set_defaults, defaults))})
        )
        return compose_contexts(context, value_context)


class ContextBaseModel(BaseModel, BaseContext):
    """Context base model."""

    @model_validator(mode="before")
    @classmethod
    def context_validate_before(
        cls, data: dict[str, Any], info: ValidationInfo
    ) -> dict[str, Any]:
        """Validate context before."""
        return cls.apply(mode="before", data=data, info=info)

    @model_validator(mode="after")
    def context_validate_after(self, info: ValidationInfo) -> Self:
        """Validate context after."""
        return self.apply(mode="after", data=self, info=info)

    @classmethod
    def apply(cls, mode: Mode | Any, data: S, info: ValidationInfo) -> S:
        """Apply a pipe to data."""
        context = Context(info.context) or Context()
        pipelines_context = (
            get_context_value(PipelinesContext, context) or PipelinesContext()
        )
        pipelines = pipelines_context.get(cls)  # pyright: ignore[reportArgumentType]
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
        for pipe in pipeline:
            if isinstance(pipe, Pipe):
                data = pipe.f(data, pipe.context_value)
                continue
            if isinstance(pipe, PipeWithInfo):
                data = pipe.f(data, pipe.context_value, info)
                continue
            if isinstance(pipe, Callable):
                data = pipe(data)
                continue
            raise ValueError("Invalid pipe.")
        return data
