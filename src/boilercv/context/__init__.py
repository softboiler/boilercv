"""Context."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from copy import copy, deepcopy
from json import loads
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Generic, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    FieldSerializationInfo,
    PydanticUserError,
    RootModel,
    SerializerFunctionWrapHandler,
    field_serializer,
    model_validator,
)
from pydantic._internal import _repr
from pydantic.main import IncEx, _object_setattr
from pydantic.root_model import RootModelRootType, _RootModelMetaclass
from pydantic_core import PydanticUndefined

from boilercv.context.types import (
    Context,
    ContextPluginSettings,
    Data_T,
    K,
    Mode,
    PluginConfigDict,
    V,
)
from boilercv.mappings import apply

CONTEXT = "context"
"""Context attribute name."""
_KWDS = "_kwds"
"""Keywords temporary key name."""
MODEL_CONFIG = "model_config"
"""Model config attribute name."""
PLUGIN_SETTINGS = "plugin_settings"
"""Model config plugin settings key."""
PLUGIN_CONTEXT = "context"
"""Plugin settings context key."""


def context_validate_before(data: Any) -> Any:
    """Validate context before."""
    if _KWDS in data:
        if isinstance(data, MutableMapping):
            data.pop(_KWDS)
            return data
        if isinstance(data, Mapping):
            return {k: v for k, v in data.items() if k != _KWDS}
    return data


class Kwds(BaseModel):
    """Keywords."""

    strict: bool | None = None
    from_attributes: bool | None = None
    context: Annotated[dict[str, Any] | None, BeforeValidator(lambda v: v or {})] = (
        Field(default_factory=dict)
    )
    mode: Mode = "python"


class ContextBase(BaseModel):
    """Context base model that guarantees context is available during validation."""

    model_config: ClassVar[PluginConfigDict[ContextPluginSettings[Context]]] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict(
            validate_default=True,
            plugin_settings=ContextPluginSettings(context=Context()),
            protected_namespaces=(),
        )
    )

    def __init__(self, /, **data: Any):
        kwds = Kwds.model_validate(data.pop(_KWDS, {}))
        self.__context_init__(data=data, kwds=kwds)

    __init__.__pydantic_base_init__ = True  # pyright: ignore[reportFunctionMemberAccess]

    def __context_init__(self, data: Any, kwds: Kwds):  # noqa: PLW3201
        """Context initializer."""
        self.__pydantic_validator__.validate_python(
            (
                apply(data, node_fun=lambda v: {**v, _KWDS: kwds})
                if isinstance(data, Mapping)
                else data
            ),
            self_instance=self,
            strict=kwds.strict,
            from_attributes=kwds.from_attributes,
            context=kwds.context,
        )

    @model_validator(mode="before")
    @classmethod
    def context_validate_before(cls, data: Any) -> Any:
        """Validate context before."""
        return context_validate_before(data)

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
            context=context or {},
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
            context=context or {},
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
        return cls.context_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            mode="python",
        )

    @classmethod
    def model_validate_strings(
        cls, obj: Any, *, strict: bool | None = None, context: Any | None = None
    ) -> Self:
        """Contextualizable string model validate."""
        return cls.context_validate(obj, strict=strict, context=context, mode="strings")

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: Any | None = None,
    ) -> Self:
        """Contextualizable JSON model validate."""
        return cls.context_validate(
            json_data, strict=strict, context=context, mode="json"
        )

    @classmethod
    def context_validate(
        cls,
        obj: Any,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        mode: Mode = "python",
    ) -> Self:
        """Validate with context."""
        kwds = Kwds(
            strict=strict, from_attributes=from_attributes, context=context, mode=mode
        )
        match kwds.mode:
            # TODO: Make `ContextBase` "json" mode go through `python` so we can propagate context
            case "json":
                return cls.__pydantic_validator__.validate_json(
                    (obj or '""') if cls.__pydantic_root_model__ else (obj or "{}"),
                    strict=kwds.strict,
                    context=kwds.context,
                )
            case "strings":
                return cls.__pydantic_validator__.validate_strings(
                    obj, strict=kwds.strict, context=kwds.context
                )
            case "python" if isinstance(obj, BaseModel):
                return obj
            case "python":
                return (
                    cls(root=obj, **{_KWDS: kwds})
                    if cls.__pydantic_root_model__
                    else cls(**obj, **{_KWDS: kwds})
                )


class ContextRoot(  # noqa: PLW1641
    ContextBase, Generic[RootModelRootType], metaclass=_RootModelMetaclass
):
    """Usage docs: https://docs.pydantic.dev/2.8/concepts/models/#rootmodel-and-custom-root-types

    A Pydantic `BaseModel` for the root object of the model.

    Attributes
    ----------
        root: The root object of the model.
        __pydantic_root_model__: Whether the model is a RootModel.
        __pydantic_private__: Private fields in the model.
        __pydantic_extra__: Extra fields in the model.

    Notes
    -----
    The original license for `RootModel` is reproduced below.

    The MIT License (MIT)

    Copyright (c) 2017 to present Pydantic Services Inc. and individual contributors.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """  # noqa: D400

    __pydantic_root_model__ = True
    __pydantic_private__ = None
    __pydantic_extra__ = None

    root: RootModelRootType

    def __init_subclass__(cls, **kwargs):
        extra = cls.model_config.get("extra")
        if extra is not None:
            raise PydanticUserError(
                "`RootModel` does not support setting `model_config['extra']`",
                code="root-model-extra",
            )
        super().__init_subclass__(**kwargs)

    def __init__(self, /, root: RootModelRootType = PydanticUndefined, **data) -> None:
        kwds = Kwds.model_validate(data.pop(_KWDS, {}))
        if data:
            if root is not PydanticUndefined:
                raise ValueError(
                    '"RootModel.__init__" accepts either a single positional argument or arbitrary keyword arguments'
                )
            root = data  # pyright: ignore[reportAssignmentType]
        self.__context_init__(data=root, kwds=kwds)

    __init__.__pydantic_base_init__ = True  # pyright: ignore[reportFunctionMemberAccess]

    @classmethod
    def model_construct(  # type: ignore
        cls, root: RootModelRootType, _fields_set: set[str] | None = None
    ) -> Self:
        """Create a new model using the provided root object and update fields set.

        Args:
            root: The root object of the model.
            _fields_set: The set of fields to be updated.

        Returns
        -------
            The new model.

        Raises
        ------
            NotImplemented: If the model is not a subclass of `RootModel`.
        """
        return super().model_construct(root=root, _fields_set=_fields_set)

    def __getstate__(self) -> dict[Any, Any]:
        return {
            "__dict__": self.__dict__,
            "__pydantic_fields_set__": self.__pydantic_fields_set__,
        }

    def __setstate__(self, state: dict[Any, Any]) -> None:
        _object_setattr(
            self, "__pydantic_fields_set__", state["__pydantic_fields_set__"]
        )
        _object_setattr(self, "__dict__", state["__dict__"])

    def __copy__(self) -> Self:
        """Returns a shallow copy of the model."""  # noqa: D401
        cls = type(self)
        m = cls.__new__(cls)
        _object_setattr(m, "__dict__", copy(self.__dict__))
        _object_setattr(
            m, "__pydantic_fields_set__", copy(self.__pydantic_fields_set__)
        )
        return m

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> Self:
        """Returns a deep copy of the model."""  # noqa: D401
        cls = type(self)
        m = cls.__new__(cls)
        _object_setattr(m, "__dict__", deepcopy(self.__dict__, memo=memo))
        # This next line doesn't need a deepcopy because __pydantic_fields_set__ is a set[str],
        # and attempting a deepcopy would be marginally slower.
        _object_setattr(
            m, "__pydantic_fields_set__", copy(self.__pydantic_fields_set__)
        )
        return m

    if TYPE_CHECKING:

        def model_dump(  # type: ignore
            self,
            *,
            mode: Literal["json", "python"] | str = "python",  # noqa: PYI051
            include: Any = None,
            exclude: Any = None,
            context: dict[str, Any] | None = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool | Literal["none", "warn", "error"] = True,
            serialize_as_any: bool = False,
        ) -> Any:
            """This method is included just to get a more accurate return type for type checkers.
            It is included in this `if TYPE_CHECKING:` block since no override is actually necessary.

            See the documentation of `BaseModel.model_dump` for more details about the arguments.

            Generally, this method will have a return type of `RootModelRootType`, assuming that `RootModelRootType` is
            not a `BaseModel` subclass. If `RootModelRootType` is a `BaseModel` subclass, then the return
            type will likely be `dict[str, Any]`, as `model_dump` calls are recursive. The return type could
            even be something different, in the case of a custom serializer.
            Thus, `Any` is used here to catch all of these cases.
            """  # noqa: D205, D401, D404
            ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RootModel):
            return NotImplemented
        return self.model_fields["root"].annotation == other.model_fields[
            "root"
        ].annotation and super().__eq__(other)

    def __repr_args__(self) -> _repr.ReprArgs:  # noqa: PLW3201
        yield "root", self.root


class RootMapping(  # noqa: PLW1641
    ContextRoot[MutableMapping[K, V]], MutableMapping[K, V], Generic[K, V]
):
    """Mapping root model with context."""

    root: MutableMapping[K, V] = Field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        return self.root == (other.root if isinstance(other, RootMapping) else other)

    # `MutableMapping` methods adapted from `collections.UserDict`, but with `data`
    # replaced by `root`and `hasattr` guard changed to equivalent `getattr(..., None)`
    # pattern in `__getitem__`. This is done to prevent inheriting directly from
    # `UserDict`, which doesn't play nicely with `pydantic.RootModel`.
    # Source: https://github.com/python/cpython/blob/7d7eec595a47a5cd67ab420164f0059eb8b9aa28/Lib/collections/__init__.py#L1121-L1211

    @classmethod
    def fromkeys(cls, iterable, value=None):  # noqa: D102
        return cls(dict.fromkeys(iterable, value))  # pyright: ignore[reportCallIssue]

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


class ContextModel(ContextBase):
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
        # TODO: De-duplicate methods on parent `ContextBase`
        context = self.context_validate_pre_init(data)
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
            cls.context_set(obj, context := cls.context_validate_pre_init(obj)),
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
                        obj.model_dump(context=cls.context_get(obj))
                        if isinstance(obj, BaseModel)
                        else obj
                    )
                ),
                CONTEXT: (context := cls.context_validate_pre_init(obj, context)),
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
    def context_validate_pre_init(
        cls, data: dict[str, Any], other: Context | None = None
    ) -> Context:
        """Validate context before model validation."""
        return {  # pyright: ignore[reportReturnType]
            k: cls._context_handlers[k].model_validate(obj=v)
            for k, v in {
                **deepcopy(cls.model_config[PLUGIN_SETTINGS][CONTEXT]),
                **cls.context_get(data),
                **(other or {}),
            }.items()
        }

    @classmethod
    def context_get(cls, data: Self | dict[str, Any]) -> Context:
        """Get context."""
        if isinstance(data, ContextModel):
            return data.context
        elif context := data.get(CONTEXT):
            return loads(context) if isinstance(context, str) else context
        return {}

    @classmethod
    def context_set(cls, data: Data_T, context: Context | None = None) -> Data_T:
        """Set context."""
        context = context or {}
        if isinstance(data, BaseModel):
            pass
        elif isinstance(data, ContextModel):
            data.context = context
        else:
            data[CONTEXT] = context
        return data
