"""Context serializers.

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

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic

from pydantic import PlainSerializer, WrapSerializer
from pydantic import model_serializer as context_model_serializer  # noqa: F401
from pydantic_core import PydanticUndefined
from pydantic_core.core_schema import SerializerFunction

from boilercv.contexts.types import Context_T_out
from boilercv.serializers.types import ContextWrapSerializerFunction, WhenUsed

if TYPE_CHECKING:

    @dataclass(slots=True, frozen=True)
    class ContextWrapSerializer(Generic[Context_T_out]):
        func: ContextWrapSerializerFunction[Context_T_out]
        return_type: Any = PydanticUndefined
        when_used: WhenUsed = "always"

    @dataclass(slots=True, frozen=True)
    class ContextPlainSerializer:
        func: SerializerFunction
        return_type: Any = PydanticUndefined
        when_used: WhenUsed = "always"


else:

    def ContextWrapSerializer(
        func: ContextWrapSerializerFunction[Context_T_out],
        return_type: Any = PydanticUndefined,
        when_used: WhenUsed = "always",
    ) -> WrapSerializer:
        return WrapSerializer(func=func, return_type=return_type, when_used=when_used)

    def ContextPlainSerializer(
        func: SerializerFunction,
        return_type: Any = PydanticUndefined,
        when_used: WhenUsed = "always",
    ) -> PlainSerializer:
        return PlainSerializer(func=func, return_type=return_type, when_used=when_used)
