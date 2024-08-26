"""Context."""

from collections.abc import Iterator, Mapping, MutableMapping
from copy import deepcopy
from json import loads
from typing import Any, ClassVar, Generic, Literal, Self

from pydantic import (
    BaseModel,
    Field,
    FieldSerializationInfo,
    RootModel,
    SerializerFunctionWrapHandler,
    field_serializer,
)
from pydantic.main import IncEx

from boilercv_pipeline.context.types import (
    Context,
    ContextPluginSettings,
    Data_T,
    K,
    PluginConfigDict,
    V,
)

CONTEXT = "context"
"""Context attribute name."""
_CONTEXT = "_context"
"""Context key."""
MODEL_CONFIG = "model_config"
"""Model config attribute name."""
PLUGIN_SETTINGS = "plugin_settings"
"""Model config plugin settings key."""
PLUGIN_CONTEXT = "context"
"""Plugin settings context key."""


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
            cls.set_context(obj, context := cls.context_validate_before(obj)),
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
                        obj.model_dump(context=cls.get_context(obj))
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
                    continue
                data[field] = {**value, CONTEXT: inner_context}
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
                **cls.get_context(data),
                **(other or {}),
            }.items()
        }

    @classmethod
    def get_context(cls, data: Self | dict[str, Any]) -> Context:
        """Get context."""
        if isinstance(data, ContextModel):
            return data.context
        elif context := data.get(CONTEXT):
            return loads(context) if isinstance(context, str) else context
        return {}

    @classmethod
    def set_context(cls, data: Data_T, context: Context | None = None) -> Data_T:
        """Set context."""
        context = context or {}
        if isinstance(data, BaseModel):
            pass
        elif isinstance(data, ContextModel):
            data.context = context
        else:
            data[CONTEXT] = context
        return data


class ContextMapping(  # noqa: PLR0904
    RootModel[MutableMapping[K, V]], MutableMapping[K, V], Generic[K, V]
):
    """Mapping root model that guarantees context is available during validation."""

    model_config: ClassVar[PluginConfigDict[ContextPluginSettings[Context]]] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict(
            validate_default=True,
            plugin_settings=ContextPluginSettings(context=Context()),
        )
    )
    root: MutableMapping[K, V] = Field(
        default_factory=lambda: dict.fromkeys([_CONTEXT])
    )
    _context_handlers: ClassVar[dict[str, type[BaseModel]]] = {}

    @classmethod
    def context_post_init(cls, context: Context) -> Context:
        """Update context after initialization."""
        return context

    def __init__(self, /, root: MutableMapping[K, V] | None = None, **data: V) -> None:  # type: ignore
        if data and root is not None:
            raise ValueError(
                '"RootModel.__init__" accepts either a single positional argument or arbitrary keyword arguments'
            )
        root: MutableMapping[K, V] = data or root or {}  # pyright: ignore[reportAssignmentType]
        context = self.context_validate_before(root)
        self.__pydantic_validator__.validate_python(
            self.context_sync_before(root, context), self_instance=self, context=context
        )
        self[_CONTEXT] = self.context_post_init(context)  # pyright: ignore[reportArgumentType]
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
    ) -> dict[K, V]:
        """Contextulizable model dump."""
        self.context_sync_after(context)
        return super().model_dump(
            mode=mode,
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            context=self[_CONTEXT],  # pyright: ignore[reportArgumentType]
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
            context=self[_CONTEXT],  # pyright: ignore[reportArgumentType]
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
            cls.set_context(obj, context := cls.context_validate_before(obj)),
            strict=strict,
            context=context,
        )
        self_instance[_CONTEXT] = self_instance.context_post_init(context)  # pyright: ignore[reportArgumentType]
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
                        obj.model_dump(context=cls.get_context(obj))
                        if isinstance(obj, BaseModel)
                        else obj
                    )
                ),
                _CONTEXT: (context := cls.context_validate_before(obj, context)),
            },
            strict=strict,
            from_attributes=from_attributes,
            context=context,
        )

    def context_sync_after(self, context: Context | None = None):
        """Sync nested contexts after validation."""
        self[_CONTEXT] = {**(self[_CONTEXT] or {}), **(context or {})}  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
        for field, inner in self.items():
            if field == _CONTEXT:
                continue
            if isinstance(inner, ContextModel):
                inner.context = inner.context_sync_after(self[_CONTEXT])  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]
            if isinstance(inner, ContextMapping):
                inner[_CONTEXT] = inner.context_sync_after(self[_CONTEXT])  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]

    @classmethod
    def context_sync_before(
        cls, data: MutableMapping[K, V], context: Context
    ) -> MutableMapping[K, V]:
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
                value = data.get(field) or {}  # pyright: ignore[reportArgumentType]
                if isinstance(value, ContextModel):
                    value.context = inner_context  # pyright: ignore[reportAttributeAccessIssue]
                    continue
                data[field] = {**value, _CONTEXT: inner_context}  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
        return data

    @classmethod
    def context_validate_before(
        cls, data: MutableMapping[K, V], other: Context | None = None
    ) -> Context:
        """Validate context before model validation."""
        return {  # pyright: ignore[reportReturnType]
            k: cls._context_handlers[k].model_validate(obj=v)
            for k, v in {
                **deepcopy(cls.model_config[PLUGIN_SETTINGS][CONTEXT]),
                **cls.get_context(data),  # pyright: ignore[reportArgumentType]
                **(other or {}),
            }.items()
        }

    @classmethod
    def get_context(cls, data: BaseModel | MutableMapping[K, V]) -> Context:
        """Get context."""
        if isinstance(data, Mapping) and (context := data.get(_CONTEXT)):  # pyright: ignore[reportArgumentType]
            return loads(context) if isinstance(context, str) else context  # pyright: ignore[reportReturnType]
        return {}

    @classmethod
    def set_context(cls, data: Data_T, context: Context | None = None) -> Data_T:
        """Set context."""
        context = context or {}
        if isinstance(data, BaseModel):
            pass
        elif isinstance(data, ContextModel):
            data.context = context
        else:
            data[_CONTEXT] = context
        return data

    # `MutableMapping` methods adapted from `collections.UserDict`, but with `data`
    # replaced by `root`and `hasattr` guard changed to equivalent `getattr(..., None)`
    # pattern in `__getitem__`. This is done to prevent inheriting directly from
    # `UserDict`, which doesn't play nicely with `pydantic.RootModel`.
    # Source: https://github.com/python/cpython/blob/7d7eec595a47a5cd67ab420164f0059eb8b9aa28/Lib/collections/__init__.py#L1121-L1211

    @classmethod
    def fromkeys(cls, iterable, value=None):  # noqa: D102
        return cls(dict.fromkeys(iterable, value))

    def __len__(self):
        return len(self.root)

    def __getitem__(self, key: K) -> V:
        if key in self.root:
            return self.root[key]
        if missing := getattr(self.__class__, "__missing__", None):
            return missing(self, key)
        raise KeyError(key)

    def __iter__(self) -> Iterator[K]:  # pyright: ignore[reportIncompatibleMethodOverride] iterate over `root` instead of `self`
        return iter(self.root)

    def __setitem__(self, key: K, item: V):
        self.root[key] = item

    def __delitem__(self, key: K):
        del self.root[key]

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key: K):  # pyright: ignore[reportIncompatibleMethodOverride]
        return key in self.root

    def __or__(self, other: BaseModel | Mapping[Any, Any] | Any) -> Self:
        if isinstance(other, Mapping) and isinstance(other, BaseModel):
            return self.model_construct(self.model_dump() | other.model_dump())
        if isinstance(other, Mapping):
            return self.model_construct(self.model_dump() | other)  # pyright: ignore[reportOperatorIssue]
        return NotImplemented

    def __ror__(self, other: BaseModel | Mapping[Any, Any] | Any) -> Self:
        if isinstance(other, Mapping) and isinstance(other, BaseModel):
            return self.model_construct(other.model_dump() | self.model_dump())
        if isinstance(other, Mapping):
            return self.model_construct(other | self.model_dump())  # pyright: ignore[reportOperatorIssue]
        return NotImplemented

    def __ior__(self, other) -> Self:
        return self | other


cm = ContextMapping[str, str | Context]({"hello": "world", CONTEXT: {}})
cm | {}
