"""Contexts."""

from __future__ import annotations

from collections import UserDict, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from itertools import chain
from typing import Any, Self

from boilercv.contexts.types import Context
from boilercv.morphs.pipes import ContextValue
from boilercv.morphs.pipes.types import CV, AnyPipe


@dataclass
class Pipelines:
    """Pipelines."""

    before: tuple[AnyPipe, ...] = field(default_factory=tuple)
    after: tuple[AnyPipe, ...] = field(default_factory=tuple)

    @classmethod
    def make(
        cls,
        before: Sequence[AnyPipe] | AnyPipe | None = None,
        after: Sequence[AnyPipe] | AnyPipe | None = None,
    ) -> Self:
        """Get validators."""
        before = () if before is None else before
        after = () if after is None else after
        bef = tuple(before) if isinstance(before, Sequence) else (before,)
        aft = tuple(after) if isinstance(after, Sequence) else (after,)
        return cls(before=bef, after=aft)


class PipelineContext(UserDict[Any, Pipelines], ContextValue):
    """Morphs."""

    def __or__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: Self | Mapping[Any, Pipelines] | Any
    ) -> Self:
        if isinstance(other, PipelineContext):
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

    def __ior__(self, other: Self | Mapping[Any, Pipelines] | Any) -> Self:
        self.data = (self | other).data
        return self


def get_context_key(value_type: type[CV]) -> str:
    """Get context keys for a type."""
    return value_type.name_to_snake()


def get_context_value(value_type: type[CV], context: PipelineCtx | None) -> CV | None:
    """Get context values for a type."""
    return (context or PipelineCtx()).get(get_context_key(value_type))  # pyright: ignore[reportReturnType]


# * MARK: Contexts


class PipelineCtx(UserDict[str, PipelineContext | ContextValue]):
    """Morphs."""

    @property
    def pipelines(self) -> PipelineContext:
        """Get pipelines."""
        context = self.get(get_context_key(PipelineContext), PipelineContext())
        return context if isinstance(context, PipelineContext) else PipelineContext()

    def __or__(self, other: PipelineCtx | Mapping[str, Any] | Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        # sourcery skip: remove-redundant-constructor-in-dict-union
        # ! This Sourcery refactoring results in an infinite loop
        if isinstance(other, PipelineCtx):
            merged = dict(self) | dict(other)
            if (morphs := get_context_value(PipelineContext, self)) is not None and (
                other_morphs := get_context_value(PipelineContext, other)
            ) is not None:
                merged[get_context_key(PipelineContext)] = morphs | other_morphs
            return type(self)(merged)
        if isinstance(other, Mapping):
            return self | type(self)(other)  # pyright: ignore[reportArgumentType]
        return NotImplemented

    def __ror__(self, other: PipelineCtx | Mapping[str, Any] | Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Mapping):
            return type(self)(other) | self
        return NotImplemented

    def __ior__(self, other: PipelineCtx | Mapping[str, Any] | Any) -> Self:
        self.data = (self | other).data
        return self


class PipelineCtxDict(Context):
    """Boilercv pipeline context."""

    pipeline: PipelineCtx


def get_pipeline_context(ctx: PipelineCtx | None = None) -> PipelineCtxDict:
    """Get pipe model context."""
    return PipelineCtxDict(pipeline=ctx or PipelineCtx())
