"""Contexts."""

from typing import Any, ClassVar, Literal, Self, Unpack

from pydantic import BaseModel, ConfigDict
from pydantic.main import IncEx

from boilercv_pipeline.contexts.types import (
    Contexts,
    DefaultPluginConfigDict,
    DefaultPluginSettings,
    PluginConfigDict,
)


def get_config(**kwds: Unpack[ConfigDict]) -> PluginConfigDict[DefaultPluginSettings]:
    """Pydantic model config with root context."""
    return {
        **DefaultPluginConfigDict(
            plugin_settings=DefaultPluginSettings(contexts=Contexts())
        ),
        "validate_default": True,
        **kwds,
    }


class ContextsBaseModel(BaseModel):
    """Base model with default context."""

    model_config: ClassVar[DefaultPluginConfigDict] = get_config()  # pyright: ignore[reportIncompatibleVariableOverride]
    _contexts_parent: Contexts = Contexts()

    @classmethod
    def contexts_merge(cls, other: Contexts | None = None) -> Contexts:
        """Combine contexts from config and optionally other contexts."""
        contexts = cls.model_config["plugin_settings"]["contexts"]
        return {**contexts, **other} if other else contexts

    def __init__(self, /, **data: Any) -> None:
        contexts = self.contexts_merge(data.get("_contexts_parent"))
        for field, info in self.model_fields.items():
            if (
                (annotation := info.annotation)
                and (model_config := getattr(annotation, "model_config", None))
                and (
                    model_config.get("plugin_settings", {}).get("contexts", {})
                    is not None
                )
            ):
                value = data.get(field) or {}
                if isinstance(value, ContextsBaseModel):
                    value._contexts_parent = contexts  # noqa: SLF001
                else:
                    data[field] = {**value, "_contexts_parent": contexts}
        self.__pydantic_validator__.validate_python(
            data, self_instance=self, context=contexts
        )

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
