"""Contexts."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from copy import copy, deepcopy
from json import loads
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, Self

from pydantic import (
    BaseModel,
    Field,
    FieldSerializationInfo,
    PydanticUserError,
    RootModel,
    field_serializer,
    model_validator,
)
from pydantic._internal import _repr
from pydantic.main import IncEx, _object_setattr
from pydantic.root_model import RootModelRootType, _RootModelMetaclass
from pydantic_core import PydanticUndefined

from boilercv.contexts.types import (
    Context,
    ContextPluginSettings,
    Data,
    Data_T,
    K,
    PluginConfigDict,
    V,
)
from boilercv.mappings import apply

CONTEXT = "context"
"""Context attribute name."""
_CONTEXT = "_context"
"""Context temporary key name."""
MODEL_CONFIG = "model_config"
"""Model config attribute name."""
PLUGIN_SETTINGS = "plugin_settings"
"""Model config plugin settings key."""


def context_validate_before(data: Data_T) -> Data_T:
    """Validate context before."""
    if isinstance(data, BaseModel) or _CONTEXT not in data:
        return data
    data.pop(_CONTEXT)
    return data


class ContextBase(BaseModel):
    """Context base model that guarantees context is available during validation."""

    model_config: ClassVar[PluginConfigDict[ContextPluginSettings[Context]]] = (  # pyright: ignore[reportIncompatibleVariableOverride]
        PluginConfigDict(
            plugin_settings=ContextPluginSettings(context=Context()),
            protected_namespaces=(),
        )
    )

    def __init__(self, /, **data: Data):
        self.__pydantic_validator__.validate_python(
            self.context_data_pre_init(data),
            self_instance=self,
            context=data.get(_CONTEXT) or Context(),
        )

    @classmethod
    def context_data_pre_init(cls, data: Data_T) -> Data_T:
        """Update data before initialization."""
        return data

    @model_validator(mode="before")
    @classmethod
    def context_validate_before(cls, data: Any) -> Any:
        """Validate context before."""
        return context_validate_before(data)

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
        context = context or Context()
        return cls.__pydantic_validator__.validate_python(
            {**obj, _CONTEXT: context},
            strict=strict,
            from_attributes=from_attributes,
            context=context,
        )

    @classmethod
    def model_validate_strings(
        cls, obj: Any, *, strict: bool | None = None, context: Any | None = None
    ) -> Self:
        """Contextualizable string model validate."""
        return cls.model_validate(
            obj=apply(obj, leaf_fun=loads), strict=strict, context=context
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
        return cls.model_validate(
            obj=loads(json_data), strict=strict, context=context
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
            context=context or Context(),
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
            context=context or Context(),
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            serialize_as_any=serialize_as_any,
        )


class ContextRoot(  # noqa: PLW1641
    ContextBase, Generic[RootModelRootType], metaclass=_RootModelMetaclass
):
    """Usage docs: https://docs.pydantic.dev/2.8/concepts/models/#rootmodel-and-custom-root-types

    A Pydantic `BaseModel` for the root object of the model.

    Attributes
    ----------
        root :
            The root object of the model.
        __pydantic_root_model__ :
            Whether the model is a RootModel.
        __pydantic_private__ :
            Private fields in the model.
        __pydantic_extra__ :
            Extra fields in the model.

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
        if data:
            if root is not PydanticUndefined:
                raise ValueError(
                    '"ContextRoot.__init__" accepts either a single positional argument or arbitrary keyword arguments'
                )
            root = data  # pyright: ignore[reportAssignmentType]
        self.__pydantic_validator__.validate_python(root, self_instance=self)

    @classmethod
    def model_construct(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, root: RootModelRootType, _fields_set: set[str] | None = None
    ) -> Self:
        """Create a new model using the provided root object and update fields set.

        Parameters
        ----------
        root
            The root object of the model.
        _fields_set
            The set of fields to be updated.

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

    def __init__(
        self,
        /,
        root: MutableMapping[K, V] = PydanticUndefined,  # pyright: ignore[reportArgumentType]
        **data,
    ) -> None:
        context = data.pop(_CONTEXT, Context())
        if data:
            if root is not PydanticUndefined:
                raise ValueError(
                    '"RootMapping.__init__" accepts either a single positional argument or arbitrary keyword arguments'
                )
            root = data  # pyright: ignore[reportAssignmentType]
        self.__pydantic_validator__.validate_python(
            self.context_data_pre_init(root, context),
            self_instance=self,
            context=context,
        )

    @classmethod
    def context_data_pre_init(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls, data: MutableMapping[K, V], context: Context
    ) -> MutableMapping[K, V]:
        """Update data before initialization."""
        if isinstance(data, BaseModel):
            return data
        return apply(data, node_fun=lambda v: {**v, _CONTEXT: context})

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
        context = context or Context()
        return cls.__pydantic_validator__.validate_python(
            {**obj, _CONTEXT: context},
            strict=strict,
            from_attributes=from_attributes,
            context=context,
        )

    @classmethod
    def from_mapping(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
    ) -> Self:
        """Create `RootMapping` from any mapping, mutable or not."""
        return cls.model_validate(
            obj=dict(obj),
            strict=strict,
            from_attributes=from_attributes,
            context=context,
        )

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

    context: Context = Context()
    _context_handlers: ClassVar[dict[str, type[BaseModel]]] = {}

    def __init__(self, /, **data: Data):
        if isinstance(data, ContextModel):
            context: Context = data.context
        elif isinstance(data, BaseModel):
            context = Context()
        else:
            context: Context = {  # pyright: ignore[reportAssignmentType]
                k: self._context_handlers[k].model_validate(obj=v)
                for k, v in {
                    **deepcopy(self.model_config[PLUGIN_SETTINGS][CONTEXT]),
                    **data.get(_CONTEXT, Context()),  # pyright: ignore[reportGeneralTypeIssues]
                    **data.get(CONTEXT, Context()),  # pyright: ignore[reportGeneralTypeIssues]
                }.items()
            }
        super().__init__(**{**data, _CONTEXT: context})  # pyright: ignore[reportArgumentType]
        self.context = self.context_post_init(context)

    @classmethod
    def context_data_pre_init(cls, data: Data_T) -> Data_T:
        """Sync nested contexts before validation."""
        if isinstance(data, BaseModel):
            return data
        for field, info in cls.model_fields.items():
            if (
                plugin_settings := deepcopy(
                    getattr(info.annotation, MODEL_CONFIG, {}).get(PLUGIN_SETTINGS, {})
                )
            ) and isinstance(plugin_settings[CONTEXT], Mapping):
                inner_context = {**plugin_settings[CONTEXT], **data[_CONTEXT]}
                value = data.get(field) or {}
                if isinstance(value, BaseModel):
                    continue
                data[field] = {**value, _CONTEXT: inner_context}
        return data

    @classmethod
    def context_post_init(cls, context: Context) -> Context:
        """Update context after initialization."""
        return context

    @field_serializer(CONTEXT, mode="plain")
    def context_ser(self, value: Any, info: FieldSerializationInfo) -> Any:
        """Serialize context."""
        context=info.context or Context()
        return {
            k: v.model_dump(
                mode=info.mode,
                by_alias=info.by_alias,
                include=info.include,
                exclude=info.exclude,
                context=context,
                exclude_unset=info.exclude_unset,
                exclude_defaults=info.exclude_defaults,
                exclude_none=info.exclude_none,
                round_trip=info.round_trip,
                serialize_as_any=info.serialize_as_any,
            )
            for k, v in (value or context).items()
        }

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
            context=context or obj[CONTEXT] or Context(),
        )

    def context_sync_after(self, context: Context | None = None):
        """Sync nested contexts after validation."""
        self.context = {**(self.context or {}), **(context or {})}
        for field in self.model_fields_set:
            if field == CONTEXT:
                continue
            if isinstance(inner := getattr(self, field), ContextModel):
                inner.context_sync_after(self.context)  # pyright: ignore[reportAttributeAccessIssue]
