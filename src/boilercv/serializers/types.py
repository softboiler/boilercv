"""Types.

Pydantic's functional serializers repurposed for context models.

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
from typing import Any, Literal, Protocol, TypeAlias, TypeVar

from pydantic import SerializationInfo, SerializerFunctionWrapHandler
from pydantic_core.core_schema import (
    FieldWrapNoInfoSerializerFunction,
    GeneralWrapNoInfoSerializerFunction,
)

from boilercv.contexts.types import Context_T_out


class ContextSerializationInfo(SerializationInfo, Protocol[Context_T_out]):
    """Pydantic validation info with a guaranteed context."""

    @property
    def context(self) -> Context_T_out: ...  # pyright: ignore[incompatibleMethodOverride]


class ContextFieldSerializationInfo(
    ContextSerializationInfo[Context_T_out], Protocol[Context_T_out]
):
    @property
    def field_name(self) -> str: ...


ContextModelPlainSerializerWithInfo: TypeAlias = Callable[
    [Any, ContextSerializationInfo[Context_T_out]], Any
]
ModelPlainSerializerWithoutInfo: TypeAlias = Callable[[Any], Any]
ContextModelPlainSerializer: TypeAlias = (
    ContextModelPlainSerializerWithInfo[Context_T_out] | ModelPlainSerializerWithoutInfo
)
ContextModelWrapSerializerWithInfo: TypeAlias = Callable[
    [Any, SerializerFunctionWrapHandler, ContextSerializationInfo[Context_T_out]], Any
]
ModelWrapSerializerWithoutInfo: TypeAlias = Callable[
    [Any, SerializerFunctionWrapHandler], Any
]
ContextModelWrapSerializer: TypeAlias = (
    ContextModelWrapSerializerWithInfo[Context_T_out] | ModelWrapSerializerWithoutInfo
)
ContextModelSerializer: TypeAlias = (
    ContextModelPlainSerializer[Context_T_out]
    | ContextModelWrapSerializer[Context_T_out]
)

# ? `Any` because higher-kinded types aren't supported
AnyContextModelPlainSerializer: TypeAlias = ContextModelPlainSerializer[Any]
ContextModelPlainSerializer_T = TypeVar(
    "ContextModelPlainSerializer_T", bound=AnyContextModelPlainSerializer
)
AnyContextModelWrapSerializer: TypeAlias = ContextModelWrapSerializer[Any]
ContextModelWrapSerializer_T = TypeVar(
    "ContextModelWrapSerializer_T", bound=AnyContextModelWrapSerializer
)

WhenUsed: TypeAlias = Literal["always", "unless-none", "json", "json-unless-none"]
GeneralContextWrapInfoSerializerFunction: TypeAlias = Callable[
    [Any, SerializerFunctionWrapHandler, ContextSerializationInfo[Context_T_out]], Any
]
FieldContextWrapInfoSerializerFunction: TypeAlias = Callable[
    [
        Any,
        Any,
        SerializerFunctionWrapHandler,
        ContextFieldSerializationInfo[Context_T_out],
    ],
    Any,
]
ContextWrapSerializerFunction: TypeAlias = (
    GeneralWrapNoInfoSerializerFunction
    | GeneralContextWrapInfoSerializerFunction[Context_T_out]
    | FieldWrapNoInfoSerializerFunction
    | FieldContextWrapInfoSerializerFunction[Context_T_out]
)
