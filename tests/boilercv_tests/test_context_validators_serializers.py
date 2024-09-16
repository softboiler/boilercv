"""Test that context validators type check."""

from typing import Annotated as Ann
from typing import Any, Self

from pydantic import (
    BaseModel,
    PlainValidator,
    SerializerFunctionWrapHandler,
    ValidatorFunctionWrapHandler,
)
from pydantic.functional_validators import ModelWrapValidatorHandler

from boilercv.contexts import ContextBase
from boilercv.contexts.types import Context, ContextPluginSettings, PluginConfigDict
from boilercv.serializers import (
    ContextPlainSerializer,
    ContextWrapSerializer,
    context_model_serializer,
)
from boilercv.serializers.types import ContextSerializationInfo
from boilercv.validators import (
    ContextAfterValidator,
    ContextBeforeValidator,
    ContextWrapValidator,
    context_field_validator,
    context_model_validator,
)
from boilercv.validators.types import ContextValidationInfo

CTX = "ctx"


class MyCtx(BaseModel):
    msg: str = "hello"


class MyContext(Context):
    ctx: MyCtx


class MyContextModel(ContextBase):
    """Context model for {mod}`~boilercv_pipeline`."""

    model_config = PluginConfigDict(
        plugin_settings=ContextPluginSettings(context=MyContext(ctx=MyCtx()))
    )


def plain(d: int) -> int:
    return d


def wrap(
    d: Any, h: ModelWrapValidatorHandler[int], i: ContextValidationInfo[MyContext]
) -> int:
    _a = i.context[CTX].msg
    return h(d)


def bef(d: Any, i: ContextValidationInfo[MyContext]) -> int:
    _a = i.context[CTX].msg
    return d


def aft(d: int, i: ContextValidationInfo[MyContext]) -> int:
    _a = i.context[CTX].msg
    return d


def swrap(
    v: int, nxt: SerializerFunctionWrapHandler, i: ContextSerializationInfo[MyContext]
) -> str:
    _a = i.context[CTX].msg
    return nxt(v)


def splain(v: int, i: ContextSerializationInfo[MyContext]) -> str:
    _a = i.context[CTX].msg
    return str(v)


class MyModel(MyContextModel, validate_default=True):
    int_p: Ann[int, PlainValidator(plain)] = 1
    int_w: Ann[int, ContextWrapValidator(wrap)] = 1
    int_b: Ann[int, ContextBeforeValidator(bef)] = 1
    int_a: Ann[int, ContextAfterValidator(aft)] = 1
    int_sw: Ann[int, ContextWrapSerializer(swrap)] = 1
    int_sp: Ann[int, ContextPlainSerializer(splain)] = 1

    @context_model_validator(mode="wrap")
    @classmethod
    def wrap(
        cls,
        d: dict[str, Any],
        h: ModelWrapValidatorHandler[Self],
        i: ContextValidationInfo[MyContext],
    ) -> Self:
        _a = i.context[CTX].msg
        return h(d)

    @context_model_validator(mode="before")
    @classmethod
    def bef(
        cls, d: dict[str, Any], i: ContextValidationInfo[MyContext]
    ) -> dict[str, Any]:
        _a = i.context[CTX].msg
        return d

    @context_model_validator(mode="after")
    def aft(self, i: ContextValidationInfo[MyContext]) -> Self:
        _a = i.context[CTX].msg
        return self

    @context_field_validator("*", mode="plain")
    @classmethod
    def fplain(cls, d: Any) -> int:
        return d

    @context_field_validator("*", mode="wrap")
    @classmethod
    def fwrap(
        cls,
        d: Any,
        h: ValidatorFunctionWrapHandler,
        i: ContextValidationInfo[MyContext],
    ) -> int:
        _a = i.context[CTX].msg
        return h(d)

    @context_field_validator("*", mode="before")
    @classmethod
    def fbef(cls, v: Any, i: ContextValidationInfo[MyContext]) -> int:
        _a = i.context[CTX].msg
        return v

    @context_field_validator("*", mode="after")
    @classmethod
    def faft(cls, v: int, i: ContextValidationInfo[MyContext]) -> int:
        _a = i.context[CTX].msg
        return v

    @context_model_serializer(mode="wrap")
    def swrap(
        self, h: SerializerFunctionWrapHandler, i: ContextSerializationInfo[MyContext]
    ) -> Self:
        _a = i.context[CTX].msg
        return h(self)

    @context_model_serializer(mode="plain")
    def splain(self, i: ContextSerializationInfo[MyContext]) -> dict[str, Any]:
        _a = i.context[CTX].msg
        return dict(self)


MyModel()
