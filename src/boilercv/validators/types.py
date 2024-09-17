"""Types.

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
from functools import partialmethod
from typing import Any, Literal, Protocol, TypeAlias, TypeVar

from pydantic import ValidationInfo, ValidatorFunctionWrapHandler
from pydantic.functional_validators import (
    FreeModelBeforeValidatorWithoutInfo,
    ModelAfterValidatorWithoutInfo,
    ModelBeforeValidatorWithoutInfo,
    ModelWrapValidatorHandler,
    ModelWrapValidatorWithoutInfo,
)
from pydantic_core.core_schema import (
    NoInfoValidatorFunction,
    NoInfoWrapValidatorFunction,
)

from boilercv.contexts.types import Context_T_in, Context_T_out

Model_T = TypeVar("Model_T")


class ContextValidationInfo(ValidationInfo, Protocol[Context_T_out]):
    @property
    def context(self) -> Context_T_out: ...


class ContextFieldValidationInfo(
    ContextValidationInfo[Context_T_out], Protocol[Context_T_out]
):
    @property
    def context(self) -> Context_T_out: ...
    @property
    def field_name(self) -> str: ...


WithInfoContextWrapValidatorFunction: TypeAlias = Callable[
    [Any, ValidatorFunctionWrapHandler, ContextValidationInfo[Context_T_out]], Any
]
WithInfoContextValidatorFunction: TypeAlias = Callable[
    [Any, ContextValidationInfo[Context_T_out]], Any
]


class ContextModelWrapValidator(Protocol[Model_T, Context_T_in]):
    def __call__(
        self,
        cls: type[Model_T],
        value: Any,
        handler: ModelWrapValidatorHandler[Model_T],
        info: ContextValidationInfo[Context_T_in],
        /,
    ) -> Model_T: ...


AnyContextModelWrapValidator: TypeAlias = (
    ContextModelWrapValidator[Model_T, Context_T_in]
    | ModelWrapValidatorWithoutInfo[Model_T]
)


class ContextFreeModelBeforeValidator(Protocol[Context_T_in]):
    def __call__(
        self, value: Any, info: ContextValidationInfo[Context_T_in], /
    ) -> Any: ...


class ContextModelBeforeValidator(Protocol[Context_T_in]):
    def __call__(
        self, cls: Any, value: Any, info: ContextValidationInfo[Context_T_in], /
    ) -> Any: ...


AnyModeBeforeValidator: TypeAlias = (
    ContextFreeModelBeforeValidator[Context_T_in]
    | ContextModelBeforeValidator[Context_T_in]
    | FreeModelBeforeValidatorWithoutInfo
    | ModelBeforeValidatorWithoutInfo
)
ContextModelAfterValidator: TypeAlias = Callable[
    [Model_T, ContextValidationInfo[Context_T_in]], Model_T
]
AnyContextModelAfterValidator: TypeAlias = (
    ContextModelAfterValidator[Model_T, Context_T_in]
    | ModelAfterValidatorWithoutInfo[Model_T]
)

Mode: TypeAlias = Literal["wrap", "before", "after"]
Wrap: TypeAlias = Literal["wrap"]
Before: TypeAlias = Literal["before"]
After: TypeAlias = Literal["after"]

FieldValidatorModes: TypeAlias = Literal["before", "after", "wrap", "plain"]
BeforePlain: TypeAlias = Literal["before", "plain"]


class OnlyValueValidatorClsMethod(Protocol):
    def __call__(self, cls: Any, value: Any, /) -> Any: ...


class V2ContextValidatorClsMethod(Protocol[Context_T_in]):
    def __call__(
        self, cls: Any, value: Any, info: ContextValidationInfo[Context_T_in], /
    ) -> Any: ...


class OnlyValueWrapValidatorClsMethod(Protocol):
    def __call__(
        self, cls: Any, value: Any, handler: ValidatorFunctionWrapHandler, /
    ) -> Any: ...


class V2ContextWrapValidatorClsMethod(Protocol[Context_T_in]):
    def __call__(
        self,
        cls: Any,
        value: Any,
        handler: ValidatorFunctionWrapHandler,
        info: ContextValidationInfo[Context_T_in],
        /,
    ) -> Any: ...


V2ContextValidator: TypeAlias = (
    V2ContextValidatorClsMethod[Context_T_in]
    | WithInfoContextValidatorFunction[Context_T_out]
    | OnlyValueValidatorClsMethod
    | NoInfoValidatorFunction
)
V2ContextWrapValidator: TypeAlias = (
    V2ContextWrapValidatorClsMethod[Context_T_in]
    | WithInfoContextWrapValidatorFunction[Context_T_out]
    | OnlyValueWrapValidatorClsMethod
    | NoInfoWrapValidatorFunction
)
PartialClsOrStaticMethod: TypeAlias = classmethod | staticmethod | partialmethod[Any]  # pyright: ignore[reportMissingTypeArgument]

# ? `Any` because higher-kinded types aren't supported
V2BeforeAfterOrPlainContextValidatorType = TypeVar(
    "V2BeforeAfterOrPlainContextValidatorType",
    bound=V2ContextValidator[Any, Any] | PartialClsOrStaticMethod,
)
V2ContextWrapValidatorType = TypeVar(
    "V2ContextWrapValidatorType",
    bound=V2ContextWrapValidator[Any, Any] | PartialClsOrStaticMethod,
)
