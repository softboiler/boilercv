"""Contexts."""

from collections.abc import Mapping
from typing import Any, ClassVar, Literal, Self

from pydantic import BaseModel
from pydantic.main import IncEx

from boilercv_pipeline.contexts.types import (
    Contexts,
    ContextsPluginSettings,
    PluginConfigDict,
)

_CONTEXTS = "_contexts"
"""Contexts attribute name."""
MODEL_CONFIG = "model_config"
"""Model config attribute name."""
PLUGIN_SETTINGS = "plugin_settings"
"""Model config plugin settings key."""
CONTEXTS = "contexts"
"""Plugin settings contexts key."""


class ContextsModel(BaseModel):
    """Model that guarantees a dictionary context is available during validation."""

    model_config: ClassVar[PluginConfigDict[ContextsPluginSettings[Contexts]]] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict(
            validate_default=True,
            plugin_settings=ContextsPluginSettings(contexts=Contexts()),
        )
    )
    _contexts: Contexts = Contexts()

    @classmethod
    def contexts_merge(cls, other: Contexts | None = None) -> Contexts:
        """Merge contexts from config with other contexts."""
        contexts = cls.model_config[PLUGIN_SETTINGS][CONTEXTS]
        return {**contexts, **other} if other else contexts

    def __init__(self, /, **data: Any):
        contexts = self.contexts_merge(data.get(_CONTEXTS))
        self.__pydantic_validator__.validate_python(
            data, self_instance=self, context=contexts
        )
        self._contexts = contexts

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
            context=self.contexts_merge(context),
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
            context=self.contexts_merge(context),
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
            context=cls.contexts_merge(context),
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
            json_data, strict=strict, context=cls.contexts_merge(context)
        )

    @classmethod
    def model_validate_strings(
        cls, obj: Any, *, strict: bool | None = None, context: Any | None = None
    ) -> Self:
        """Contextualizable string model validate."""
        return super().model_validate_strings(
            obj, strict=strict, context=cls.contexts_merge(context)
        )


class ContextsMergeModel(ContextsModel):
    """Contexts model that merges contexts to sub-values."""

    def __init__(self, /, **data: Any) -> None:
        contexts = self.contexts_merge(data.get(_CONTEXTS))
        for field, info in self.model_fields.items():
            if (
                plugin_settings := (
                    getattr(info.annotation, MODEL_CONFIG, {}).get(PLUGIN_SETTINGS, {})
                )
            ) and isinstance(
                (inner_contexts := plugin_settings.get(CONTEXTS)), Mapping
            ):
                inner_contexts = {**inner_contexts, **contexts}
                value = data.get(field) or {}
                if isinstance(value, ContextsModel):
                    value._contexts = inner_contexts  # pyright: ignore[reportAttributeAccessIssue]  # noqa: SLF001
                else:
                    data[field] = {**value, _CONTEXTS: inner_contexts}
        self.__pydantic_validator__.validate_python(
            data, self_instance=self, context=contexts
        )
        self._contexts = contexts
