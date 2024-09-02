"""Pipelines."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from functools import partial
from itertools import chain
from typing import Any, ClassVar, Generic, Self, get_args

from pydantic import BaseModel, model_validator

from boilercv.contexts import (
    CONTEXT,
    PLUGIN_SETTINGS,
    ContextBase,
    context_validate_before,
)
from boilercv.contexts.types import ContextPluginSettings, PluginConfigDict
from boilercv.morphs.morphs import Morph
from boilercv.pipelines.contexts import (
    PipelineContext,
    PipelineCtx,
    PipelineCtxDict,
    Pipelines,
    get_context_value,
    get_pipeline_context,
)
from boilercv.pipelines.contexts.types import PipelineConfigDict, PipelineValidationInfo
from boilercv.pipelines.types import (
    K,
    LiteralGenericAlias,
    Mode,
    T,
    UnionGenericAlias,
    V,
)
from boilercv.pipes import ContextValue, Pipe, PipeWithInfo
from boilercv.pipes.types import AnyPipe

PIPELINE = "pipeline"
"""Pipe model context key."""


class PipelineBase(ContextBase):
    """Pipeline base model."""

    model_config: ClassVar[PipelineConfigDict] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict({
            PLUGIN_SETTINGS: ContextPluginSettings({
                CONTEXT: PipelineCtxDict({PIPELINE: PipelineCtx()})
            })
        })
    )

    @model_validator(mode="before")
    @classmethod
    def morph_validate_before(
        cls, data: dict[str, Any], info: PipelineValidationInfo
    ) -> dict[str, Any]:
        """Validate context before."""
        return cls.apply(mode="before", data=context_validate_before(data), info=info)

    @model_validator(mode="after")
    def morph_validate_after(self, info: PipelineValidationInfo) -> Self:
        """Validate context after."""
        return self.apply(mode="after", data=self, info=info)

    @classmethod
    def apply(cls, mode: Mode | Any, data: T, info: PipelineValidationInfo) -> T:
        """Apply a pipe to data."""
        context = info.context[PIPELINE]
        pipelines_context = (
            get_context_value(PipelineContext, context) or PipelineContext()
        )
        pipelines = pipelines_context.get(cls)
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


# * MARK: Contextualized morph


class Pipeline(Morph[K, V], Generic[K, V]):
    """Pipeline model."""

    model_config: ClassVar[PipelineConfigDict] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict({
            PLUGIN_SETTINGS: ContextPluginSettings({
                CONTEXT: PipelineCtxDict({PIPELINE: PipelineCtx()})
            })
        })
    )

    @model_validator(mode="before")
    @classmethod
    def morph_validate_before(
        cls, data: dict[K, V], info: PipelineValidationInfo
    ) -> dict[K, V]:
        """Validate context before."""
        return cls.apply(mode="before", data=context_validate_before(data), info=info)

    @model_validator(mode="after")
    def morph_validate_after(self, info: PipelineValidationInfo) -> Self:
        """Validate context after."""
        return self.apply(mode="after", data=self, info=info)

    @classmethod
    def apply(cls, mode: Mode, data: T, info: PipelineValidationInfo) -> T:  # noqa: C901, PLR0912
        """Apply a pipe to data."""
        context = info.context[PIPELINE]
        pipelines_context = (
            get_context_value(PipelineContext, context) or PipelineContext()
        )
        pipelines = pipelines_context.get(cls)
        if pipelines is None:
            return data
        if mode == "before":
            pipeline = pipelines.before
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
        pipeline = pipelines.after
        if not pipeline:
            return data
        for pipe in pipeline:
            if not pipeline:
                return data
            if isinstance(pipe, Pipe):
                data = data.morph_cpipe(pipe.f, context, pipe.context_value)  # pyright: ignore[reportAttributeAccessIssue]
                continue
            if isinstance(pipe, PipeWithInfo):
                data = data.morph_cpipe(pipe.f, context, pipe.context_value, info)  # pyright: ignore[reportAttributeAccessIssue]
                continue
            if isinstance(pipe, Callable):
                data = data.morph_cpipe(pipe, context)  # pyright: ignore[reportAttributeAccessIssue]
                continue
            raise ValueError("Invalid pipe.")
        return data

    @classmethod
    def compose_defaults(
        cls,
        mapping: dict[K, V | BaseModel] | None = None,
        keys: tuple[K, ...] | None = None,
        value: V | BaseModel | None = None,
        value_copier: Callable[[V | BaseModel], V | BaseModel] = lambda v: v,
        factory: Callable[..., Any] | None = None,
        value_model: type[Pipeline[K, V] | PipelineBase | BaseModel] | None = None,
        value_context: PipelineCtx | None = None,
    ) -> PipelineCtx:
        """Compose defaults."""
        k, v = cls.morph_get_inner_types()
        if (
            not keys
            and isinstance(k, UnionGenericAlias)
            and all(isinstance(t, LiteralGenericAlias) for t in get_args(k))
        ):
            keys = tuple(chain.from_iterable([get_args(t) for t in get_args(k)]))
        if not keys and isinstance(k, LiteralGenericAlias):
            keys = get_args(k)
        with suppress(TypeError):
            if issubclass(v, BaseModel):
                value_model = value_model or v
        keys = keys or get_args(cls.morph_get_inner_types().key)
        if value_model:
            factory = (
                partial(
                    value_model.model_validate,
                    context=get_pipeline_context(value_context),
                )
                if issubclass(value_model, Pipeline | PipelineBase)
                else partial(
                    value_model.model_validate,
                    obj={},
                    context=get_pipeline_context(value_context),
                )
            )
        defaults = (
            Defaults(mapping=mapping, value_copier=value_copier)
            if mapping
            else Defaults(
                keys=keys or (), value=value, factory=factory, value_copier=value_copier
            )
        )
        return compose_contexts(
            make_pipelines(cls, before=[Pipe(set_defaults, defaults)]),
            value_context or PipelineCtx(),
        )


# * MARK: Context values


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
    value_copier: Callable[[V], V] | None = lambda v: v
    """Method to copy the default value."""


# * MARK: Context handlers


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


def compose_contexts(*contexts: PipelineCtx) -> PipelineCtx:
    """Compose contexts."""
    context = PipelineCtx()
    for ctx in contexts:
        context |= ctx
    return context


def make_pipelines(
    typ: type,
    /,
    before: Sequence[AnyPipe] | AnyPipe | None = None,
    after: Sequence[AnyPipe] | AnyPipe | None = None,
) -> PipelineCtx:
    """Compose defaults."""
    return compose_context(
        PipelineContext({typ: Pipelines.make(before=before, after=after)})
    )


def compose_context(*context_values: ContextValue) -> PipelineCtx:
    """Compose inner contexts."""
    return PipelineCtx({
        context_value.name_to_snake(): context_value for context_value in context_values
    })
