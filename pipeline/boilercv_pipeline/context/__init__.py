"""Context."""

from collections.abc import Mapping
from typing import Any, ClassVar, Literal, Self

from pydantic import BaseModel
from pydantic.main import IncEx

from boilercv_pipeline.context.types import (
    Context,
    ContextPluginSettings,
    PluginConfigDict,
)

_CONTEXT = "_context"
"""Context attribute name."""
MODEL_CONFIG = "model_config"
"""Model config attribute name."""
PLUGIN_SETTINGS = "plugin_settings"
"""Model config plugin settings key."""
CONTEXT = "context"
"""Plugin settings context key."""


class ContextModel(BaseModel):
    """Model that guarantees a dictionary context is available during validation."""

    model_config: ClassVar[PluginConfigDict[ContextPluginSettings[Context]]] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict(
            validate_default=True,
            plugin_settings=ContextPluginSettings(context=Context()),
        )
    )
    _context: Context = Context()

    @classmethod
    def context_merge(cls, other: Context | None = None) -> Context:
        """Merge context from config with other context."""
        context = cls.model_config[PLUGIN_SETTINGS][CONTEXT]
        return {**context, **other} if other else context

    def __init__(self, /, **data: Any):
        context = self.context_merge(data.get(_CONTEXT))
        self.__pydantic_validator__.validate_python(
            data, self_instance=self, context=context
        )
        self._context = context

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",  # noqa: PYI051
        include: IncEx = None,
        exclude: IncEx = None,
        context: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        """Contextulizable model dump."""
        return super().model_dump(
            mode=mode,
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            context=self.context_merge(context),
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )

    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        include: IncEx = None,
        exclude: IncEx = None,
        context: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal["none", "warn", "error"] = True,
        serialize_as_any: bool = False,
    ) -> str:
        """Contextulizable JSON model dump."""
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            context=self.context_merge(context),
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
    ) -> Self:
        """Contextualizable model validate."""
        return super().model_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=cls.context_merge(context),
        )

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: Any | None = None,
    ) -> Self:
        """Contextualizable JSON model validate."""
        return super().model_validate_json(
            json_data, strict=strict, context=cls.context_merge(context)
        )

    @classmethod
    def model_validate_strings(
        cls, obj: Any, *, strict: bool | None = None, context: Any | None = None
    ) -> Self:
        """Contextualizable string model validate."""
        return super().model_validate_strings(
            obj, strict=strict, context=cls.context_merge(context)
        )


class ContextMergeModel(ContextModel):
    """Context model that merges context to sub-values."""

    def __init__(self, /, **data: Any) -> None:
        context = self.context_merge(data.get(_CONTEXT))
        for field, info in self.model_fields.items():
            if (
                plugin_settings := (
                    getattr(info.annotation, MODEL_CONFIG, {}).get(PLUGIN_SETTINGS, {})
                )
            ) and isinstance((inner_context := plugin_settings.get(CONTEXT)), Mapping):
                inner_context = {**inner_context, **context}
                value = data.get(field) or {}
                if isinstance(value, ContextModel):
                    value._context = inner_context  # pyright: ignore[reportAttributeAccessIssue]  # noqa: SLF001
                else:
                    data[field] = {**value, _CONTEXT: inner_context}
        self.__pydantic_validator__.validate_python(
            data, self_instance=self, context=context
        )
        self._context = context
