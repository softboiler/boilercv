"""Contexts."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from copy import copy, deepcopy
from json import loads
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, Self

from pydantic import BaseModel, Field, PydanticUserError, RootModel, model_validator
from pydantic._internal import _repr
from pydantic.fields import FieldInfo
from pydantic.main import IncEx, _object_setattr
from pydantic.root_model import RootModelRootType, _RootModelMetaclass
from pydantic_core import PydanticUndefined

from boilercv.contexts.types import (
    Context,
    ContextNode,
    ContextPluginSettings,
    ContextTree,
    Data,
    Data_T,
    K,
    PluginConfigDict,
    V,
    ValidationInfo,
)
from boilercv.mappings import apply, filt

CONFIG = "config"
"""Config key."""
_CONTEXT_TREE = "context_tree"
"""Context tree key."""
PLUGINS = "plugins"
"""Plugin settings key."""
CONTEXT = "context"
"""Context attribute name."""
ROOT = "root"
"""Root field name."""
_CONTEXT = "_context"
"""Context temporary key name."""
MODEL_CONFIG = "model_config"
"""Model config attribute name."""
MODEL_FIELDS = "model_fields"
"""Model fields attribute name."""
PLUGIN_SETTINGS = "plugin_settings"
"""Model config plugin settings key."""

DEFAULT_PLUGIN_CONFIG_DICT = PluginConfigDict(
    plugin_settings=ContextPluginSettings(context=Context()), protected_namespaces=()
)


def context_validate_before(data: Data_T) -> Data_T:
    """Validate context before."""
    if not isinstance(data, BaseModel) and _CONTEXT in data:
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
        self.__context_init__(data=data)

    def __context_init__(self, data: Data, context: Context | None = None):  # noqa: PLW3201
        if not isinstance(data, BaseModel):
            data = self.context_pre_init(data, context)
            context = {**data.get(_CONTEXT, Context()), **(context or Context())}
        self.__pydantic_validator__.validate_python(
            input=data, self_instance=self, context=context
        )

    @classmethod
    def context_get(
        cls,
        data: Data,
        context: Context | None = None,
        context_base: Context | None = None,
    ) -> Context:
        """Get context from data."""
        return (
            Context()
            if isinstance(data, BaseModel)
            else {
                **(
                    context_base or deepcopy(cls.model_config[PLUGIN_SETTINGS][CONTEXT])
                ),
                **data.get(_CONTEXT, Context()),
                **(context or Context()),
            }
        )

    # TODO: This indiscriminately applies contexts to mappings which may not be an
    # ..... actual model. Yet the context-aware `context_pre_init` doesn't handle
    # ..... root models. This is necessary for equations models to work.
    @classmethod
    def context_pre_init(cls, data: Data_T, context: Context | None = None) -> Data_T:
        """Sync nested contexts before validation."""
        if isinstance(data, BaseModel):
            return data
        context = cls.context_get(data, context)
        return apply(  # pyright: ignore[reportReturnType]
            {**data, _CONTEXT: context},
            skip_key=lambda k: k == _CONTEXT,
            skip_node=lambda v: isinstance(v, BaseModel),
            node_fun=lambda v: {
                **v,
                _CONTEXT: {**data.get(_CONTEXT, Context()), **context},
            },
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
        context = context or Context()
        return cls.__pydantic_validator__.validate_python(
            input=cls.context_pre_init(obj, context),
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
        return cls.model_validate(obj=loads(json_data), strict=strict, context=context)

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",  # noqa: PYI051
        include: IncEx | None = None,
        exclude: IncEx | None = None,
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
        include: IncEx | None = None,
        exclude: IncEx | None = None,
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

    def __init__(
        self, /, root: RootModelRootType | Any = PydanticUndefined, **data: Any
    ) -> None:
        if data:
            if root is not PydanticUndefined:
                raise ValueError(
                    '"ContextRoot.__init__" accepts either a single positional argument or arbitrary keyword arguments'
                )
            root = data
        self.__pydantic_validator__.validate_python(
            input=root, self_instance=self, context=Context()
        )

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

    @model_validator(mode="before")
    @classmethod
    def context_validate_before(cls, data: Any) -> Any:
        """Validate context before."""
        return context_validate_before(data)

    def __init__(
        self,
        /,
        root: MutableMapping[K, V] | PydanticUndefined = PydanticUndefined,
        **data: V,
    ) -> None:
        if data:
            if root is not PydanticUndefined:
                raise ValueError(
                    '"RootMapping.__init__" accepts either a single positional argument or arbitrary keyword arguments'
                )
            root = data
        # ? `reportArgumentType` raised because `K` isn't bound by `str`, necessary to
        # ? allow subclasses to use literal strings for `K`.
        context = root.get(_CONTEXT, Context())  # pyright: ignore[reportArgumentType]
        # ?`reportArgumentType` raised because of unexpressible root/context types
        self.__context_init__(data=root, context=context)  # pyright: ignore[reportArgumentType]

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

    # ?`MutableMapping` methods adapted from `collections.UserDict`, but with `data`
    # ? replaced by `root`and `hasattr` guard changed to equivalent
    # ? `getattr(..., None)` pattern in `__getitem__`. This is done to prevent
    # ? inheriting directly from `UserDict`, which doesn't play nicely with
    # ? `pydantic.RootModel`.
    # ? https://github.com/python/cpython/blob/7d7eec595a47a5cd67ab420164f0059eb8b9aa28/Lib/collections/__init__.py#L1121-L1211

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

    # ? Iterate over `root` instead of `self`
    def __iter__(self) -> Iterator[K]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return iter(self.root)

    def __setitem__(self, key: K, item: V):
        self.root[key] = item

    def __delitem__(self, key: K):
        del self.root[key]

    # ? Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key: K):  # pyright: ignore[reportIncompatibleMethodOverride]
        return key in self.root

    def __or__(self, other: BaseModel | Mapping[Any, Any] | Any) -> Self:
        if isinstance(other, Mapping) and isinstance(other, BaseModel):
            return self.model_construct(self.model_dump() | other.model_dump())
        if isinstance(other, Mapping):
            return self.model_construct(self.model_dump() | other)
        return NotImplemented

    def __ror__(self, other: BaseModel | Mapping[Any, Any] | Any) -> Self:
        if isinstance(other, Mapping) and isinstance(other, BaseModel):
            return self.model_construct(other.model_dump() | self.model_dump())
        if isinstance(other, Mapping):
            return self.model_construct(other | self.model_dump())
        return NotImplemented

    def __ior__(self, other) -> Self:
        return self | other


def get_context_tree(klass: type[BaseModel] | Any = None) -> ContextNode:
    """Get context tree."""
    nodes: ContextTree = {}
    fields: dict[str, FieldInfo] = getattr(klass, MODEL_FIELDS, {})
    for f, i in fields.items():
        if f not in [ROOT, CONTEXT] and filt(node := get_context_tree(i.annotation)):
            nodes[f] = node
    config = deepcopy(getattr(klass, MODEL_CONFIG, {})) if klass else {}  # pyright: ignore[reportArgumentType]
    return ContextNode(
        config=config,  # pyright: ignore[reportArgumentType]
        plugins=(p := config.get(PLUGIN_SETTINGS, {})),
        context=p.get(CONTEXT, {}),
        context_tree=nodes,
    )


class ContextModel(ContextBase):
    """Model that guarantees a dictionary context is available during validation."""

    context: Context = Context()

    @classmethod
    def context_get(
        cls,
        data: Data,
        context: Context | None = None,
        context_base: Context | None = None,
    ) -> Context:
        """Get context from data."""
        if isinstance(data, ContextModel):
            return data.context
        elif isinstance(data, BaseModel):
            return Context()
        else:
            return {
                **(
                    context_base or deepcopy(cls.model_config[PLUGIN_SETTINGS][CONTEXT])
                ),
                **data.get(_CONTEXT, Context()),
                **data.get(CONTEXT, Context()),
                **(context or Context()),
            }

    @model_validator(mode="before")
    @classmethod
    def validate_context_bef(
        cls, data: dict[str, Any], info: ValidationInfo[Context]
    ) -> dict[str, Any]:
        """Set context after validation."""
        data[CONTEXT] = info.context
        return data

    @classmethod
    def context_pre_init(cls, data: Data_T, context: Context | None = None) -> Data_T:
        """Sync nested contexts before validation."""
        if isinstance(data, BaseModel):
            return data
        return cls.context_get_data(
            data,
            tree=get_context_tree(cls)[_CONTEXT_TREE],
            context=cls.context_get(data, context),
        )

    @classmethod
    def context_get_data(
        cls, data: MutableMapping[str, Any], tree: ContextTree, context: Context
    ) -> dict[str, Any]:
        """Get data."""
        data = copy(data)
        for field, node in tree.items():
            inner_data = data.get(field) or {}
            if isinstance(inner_data, BaseModel):
                continue
            data[field] = cls.context_get_data(
                data=inner_data,
                tree=node[_CONTEXT_TREE],
                context=cls.context_get(data, context, context_base=node[CONTEXT]),
            )
        return {**data, _CONTEXT: context}

    def context_get_own(
        self,
        data: Data,
        context: Context | None = None,
        context_base: Context | None = None,
    ) -> Context:
        """Get context from self."""
        return {**self.context, **self.context_get(data, context, context_base)}

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",  # noqa: PYI051
        include: IncEx | None = None,
        exclude: IncEx | None = None,
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
            context=self.context_get_own(self, context),
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
        include: IncEx | None = None,
        exclude: IncEx | None = None,
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
            context=self.context_get_own(self, context),
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
            context=cls.context_get(obj, context),
        )
