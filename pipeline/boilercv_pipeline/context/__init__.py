"""Context."""

from collections.abc import Mapping
from copy import deepcopy
from json import loads
from typing import Any, ClassVar, Literal, Self

from pydantic import (
    BaseModel,
    FieldSerializationInfo,
    SerializerFunctionWrapHandler,
    field_serializer,
)
from pydantic.main import IncEx

from boilercv_pipeline.context.types import (
    Context,
    ContextPluginSettings,
    Data_T,
    PluginConfigDict,
)

CONTEXT = "context"
"""Context attribute name."""
MODEL_CONFIG = "model_config"
"""Model config attribute name."""
PLUGIN_SETTINGS = "plugin_settings"
"""Model config plugin settings key."""
PLUGIN_CONTEXT = "context"
"""Plugin settings context key."""


def get_context(data: BaseModel | dict[str, Any]) -> Context:
    """Get context."""
    if isinstance(data, ContextModel):
        return data.context
    elif isinstance(data, Mapping) and (context := data.get(CONTEXT)):
        return loads(context) if isinstance(context, str) else context
    return {}


def set_context(data: Data_T, context: Context | None = None) -> Data_T:
    """Set context."""
    context = context or {}
    if isinstance(data, ContextModel):
        data.context = context
    elif isinstance(data, Mapping):
        data[CONTEXT] = context
    return data


class ContextModel(BaseModel):
    """Model that guarantees a dictionary context is available during validation."""

    model_config: ClassVar[PluginConfigDict[ContextPluginSettings[Context]]] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict(
            validate_default=True,
            plugin_settings=ContextPluginSettings(context=Context()),
        )
    )
    context: Context = Context()
    _context_handlers: ClassVar[dict[str, type[BaseModel]]] = {}

    @field_serializer(CONTEXT, mode="wrap")
    def context_ser(
        self,
        value: Any,
        nxt: SerializerFunctionWrapHandler,
        info: FieldSerializationInfo,
    ) -> Any:
        """Serialize context."""
        return {k: nxt(v) for k, v in (value or info.context or {}).items()}

    @classmethod
    def context_post_init(cls, context: Context) -> Context:
        """Update context after initialization."""
        return context

    def __init__(self, /, **data: Any):
        context = self.context_validate_before(data)
        self.__pydantic_validator__.validate_python(
            self.context_sync_before(data, context), self_instance=self, context=context
        )
        self.context = self.context_post_init(context)
        self.context_sync_after(context)

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
        self.context_sync_after(context)
        return super().model_dump(
            mode=mode,
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            context=self.context,
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
        self.context_sync_after(context)
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            context=self.context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )

    @classmethod
    def model_validate_strings(
        cls, obj: Any, *, strict: bool | None = None, context: Any | None = None
    ) -> Self:
        """Contextualizable string model validate."""
        self_instance = super().model_validate_strings(
            set_context(obj, context := cls.context_validate_before(obj)),
            strict=strict,
            context=context,
        )
        self_instance.context = self_instance.context_post_init(context)
        self_instance.context_sync_after(context)
        return self_instance

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: Any | None = None,
    ) -> Self:
        """Contextualizable JSON model validate."""
        return cls.model_validate(
            obj=loads(json_data or "{}"), strict=strict, context=context
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
            obj={
                **(
                    obj := (
                        obj.model_dump(context=get_context(obj))
                        if isinstance(obj, BaseModel)
                        else obj
                    )
                ),
                CONTEXT: (context := cls.context_validate_before(obj, context)),
            },
            strict=strict,
            from_attributes=from_attributes,
            context=context,
        )

    def context_sync_after(self, context: Context | None = None):
        """Sync nested contexts after validation."""
        self.context = {**(self.context or {}), **(context or {})}
        for field in self.model_fields_set:
            if field == CONTEXT:
                continue
            if isinstance(inner := getattr(self, field), ContextModel):
                inner.context = inner.context_sync_after(self.context)  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def context_sync_before(
        cls, data: dict[str, Any], context: Context
    ) -> dict[str, Any]:
        """Sync nested contexts before validation."""
        for field, info in cls.model_fields.items():
            if (
                plugin_settings := deepcopy(
                    getattr(info.annotation, MODEL_CONFIG, {}).get(PLUGIN_SETTINGS, {})
                )
            ) and isinstance(
                (inner_context_config := plugin_settings.get(PLUGIN_CONTEXT)), Mapping
            ):
                inner_context = {**inner_context_config, **context}
                value = data.get(field) or {}
                if isinstance(value, ContextModel):
                    value.context = inner_context  # pyright: ignore[reportAttributeAccessIssue]
                else:
                    data[field] = {**value, CONTEXT: inner_context}
                continue
        return data

    @classmethod
    def context_validate_before(
        cls, data: dict[str, Any], other: Context | None = None
    ) -> Context:
        """Validate context before model validation."""
        return {  # pyright: ignore[reportReturnType]
            k: cls._context_handlers[k].model_validate(obj=v)
            for k, v in {
                **deepcopy(cls.model_config[PLUGIN_SETTINGS][CONTEXT]),
                **get_context(data),
                **(other or {}),
            }.items()
        }
