"""Context validators.

Pydantic's functional validators repurposed for context models.

Notes
-----
The original license is reproduced below.

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
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, overload

from pydantic import (
    AfterValidator,
    BeforeValidator,
    WrapValidator,
    field_validator,
    model_validator,
)
from pydantic._internal._decorators import (
    ModelValidatorDecoratorInfo,
    PydanticDescriptorProxy,
)
from pydantic_core import PydanticUndefined
from pydantic_core.core_schema import (
    NoInfoValidatorFunction,
    NoInfoWrapValidatorFunction,
)

from boilercv.contexts.types import Context_T_in, Context_T_out
from boilercv.validators.types import (
    After,
    AnyContextModelAfterValidator,
    AnyContextModelWrapValidator,
    AnyModeBeforeValidator,
    Before,
    BeforePlain,
    FieldValidatorModes,
    Mode,
    Model_T,
    V2BeforeAfterOrPlainContextValidatorType,
    V2ContextWrapValidatorType,
    WithInfoContextValidatorFunction,
    WithInfoContextWrapValidatorFunction,
    Wrap,
)


@overload
def context_model_validator(
    *, mode: Wrap
) -> Callable[
    [AnyContextModelWrapValidator[Model_T, Context_T_in]],
    PydanticDescriptorProxy[ModelValidatorDecoratorInfo],
]: ...
@overload
def context_model_validator(
    *, mode: Before
) -> Callable[
    [AnyModeBeforeValidator[Context_T_in]],
    PydanticDescriptorProxy[ModelValidatorDecoratorInfo],
]: ...
@overload
def context_model_validator(
    *, mode: After
) -> Callable[
    [AnyContextModelAfterValidator[Model_T, Context_T_in]],
    PydanticDescriptorProxy[ModelValidatorDecoratorInfo],
]: ...
def context_model_validator(*, mode: Mode) -> Any:
    return model_validator(mode=mode)


@overload
def context_field_validator(
    field: str,
    /,
    *fields: str,
    mode: Wrap,
    check_fields: bool | None = ...,
    json_schema_input_type: Any = ...,
) -> Callable[[V2ContextWrapValidatorType], V2ContextWrapValidatorType]: ...
@overload
def context_field_validator(
    field: str,
    /,
    *fields: str,
    mode: BeforePlain,
    check_fields: bool | None = ...,
    json_schema_input_type: Any = ...,
) -> Callable[
    [V2BeforeAfterOrPlainContextValidatorType], V2BeforeAfterOrPlainContextValidatorType
]: ...
@overload
def context_field_validator(
    field: str,
    /,
    *fields: str,
    mode: After = ...,
    check_fields: bool | None = ...,
    json_schema_input_type: Any = ...,
) -> Callable[
    [V2BeforeAfterOrPlainContextValidatorType], V2BeforeAfterOrPlainContextValidatorType
]: ...
def context_field_validator(
    field: str,
    /,
    *fields: str,
    mode: FieldValidatorModes = "after",
    check_fields: bool | None = None,
    json_schema_input_type: Any = PydanticUndefined,
) -> Callable[[Any], Any]:
    return field_validator(  # pyright: ignore[reportCallIssue]
        field,
        *fields,
        mode=mode,  # pyright: ignore[reportArgumentType]
        check_fields=check_fields,
        json_schema_input_type=json_schema_input_type,
    )


if TYPE_CHECKING:

    @dataclass(slots=True, frozen=True)
    class ContextWrapValidator(Generic[Context_T_out]):
        func: (
            NoInfoWrapValidatorFunction
            | WithInfoContextWrapValidatorFunction[Context_T_out]
        )

    @dataclass(slots=True, frozen=True)
    class ContextBeforeValidator(Generic[Context_T_out]):
        func: NoInfoValidatorFunction | WithInfoContextValidatorFunction[Context_T_out]

    @dataclass(slots=True, frozen=True)
    class ContextAfterValidator(Generic[Context_T_out]):
        func: NoInfoValidatorFunction | WithInfoContextValidatorFunction[Context_T_out]

else:

    def ContextWrapValidator(
        func: (
            NoInfoWrapValidatorFunction
            | WithInfoContextWrapValidatorFunction[Context_T_out]
        ),
    ) -> WrapValidator:
        return WrapValidator(func)  # pyright: ignore[reportArgumentType]

    def ContextBeforeValidator(
        func: NoInfoValidatorFunction | WithInfoContextValidatorFunction[Context_T_out],
    ) -> BeforeValidator:
        return BeforeValidator(func)  # pyright: ignore[reportArgumentType]

    def ContextAfterValidator(
        func: NoInfoValidatorFunction | WithInfoContextValidatorFunction[Context_T_out],
    ) -> AfterValidator:
        return AfterValidator(func)  # pyright: ignore[reportArgumentType]
