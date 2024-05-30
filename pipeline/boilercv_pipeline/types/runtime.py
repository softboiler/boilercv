"""Type annotations used at runtime in {mod}`boilercv_pipeline`."""

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Annotated, Any, Literal, TypeAlias, TypeVar, overload

import sympy
from pydantic import (
    AfterValidator,
    BeforeValidator,
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
    WrapValidator,
)
from sympy import sympify

from boilercv.morphs.types.runtime import ContextValue
from boilercv_pipeline.types import K

# * MARK: `TypeVar`s and `TypeAlias`es for annotations

CV = TypeVar("CV", bound=ContextValue, contravariant=True)
"""Context value."""
SK = TypeVar("SK")
"""Symbol key."""

Validator: TypeAlias = Literal["before", "wrap", "after", "plain"]
"""Validators."""

# * MARK: Annotation parts


def contextualize(context_value_type: type[CV]):
    """Contextualize a function."""

    def wrapper(f) -> Callable[[Any, ValidationInfo], Any]:
        def validator(
            v: Callable[[str, CV, ValidationInfo], Any], info: ValidationInfo, /
        ):
            key = context_value_type.name_to_snake()
            context = info.context or {}
            if not context:
                raise ValueError(
                    f"No context given. Expected value at '{key}' of type '{context_value_type}'."
                )
            context_value = context.get(key)
            if not context_value:
                raise ValueError(
                    f"No context value at {key}. Expected context value at '{key}' of type '{context_value_type}'."
                )
            if not isinstance(context_value, context_value_type):
                raise ValueError(  # noqa: TRY004 so Pydantic catches it
                    f"Context value at {key} not of expected type '{context_value_type}'."
                )
            return f(v, context_value)

        return validator

    return wrapper


@dataclass
class SympifyParams(ContextValue):
    """Sympify parameters."""

    locals: dict[str, Any] | None = None
    convert_xor: bool | None = None
    strict: bool = False
    rational: bool = False
    evaluate: bool | None = None


def sympify_expr(expr: str, sympify_params: SympifyParams) -> Any:
    """Sympify an expression from local variables."""
    return sympify(expr, **asdict(sympify_params))


validate_expr = contextualize(SympifyParams)(sympify_expr)

VALIDATORS: dict[Validator, Any] = {
    "before": BeforeValidator,
    "wrap": WrapValidator,
    "after": AfterValidator,
    "plain": PlainValidator,
}
"""Validators."""


@overload
def TypeValidator(typ: type[K], mode: Literal["before"]) -> BeforeValidator: ...
@overload
def TypeValidator(typ: type[K], mode: Literal["wrap"]) -> WrapValidator: ...
@overload
def TypeValidator(typ: type[K], mode: Literal["after"]) -> AfterValidator: ...
@overload
def TypeValidator(typ: type[K], mode: Literal["plain"]) -> PlainValidator: ...
@overload
def TypeValidator(typ: type[K]) -> PlainValidator: ...
def TypeValidator(typ: type[K], mode: Validator = "plain") -> Any:  # noqa: N802; Can't inherit from frozen
    """Validate type."""

    def validate(v: K) -> K:
        if isinstance(v, typ):
            return v
        raise ValueError(f"Input should be a valid {typ}")

    return VALIDATORS[mode](validate)


def _str(v: Any) -> str:
    """Stringify."""
    return str(v)


def StrSerializer(  # noqa: N802; Can't inherit from frozen
    when_used: Literal["always", "unless-none", "json", "json-unless-none"] = "always",
) -> PlainSerializer:
    """Serialize as string."""
    return PlainSerializer(_str, when_used=when_used)


# * MARK: Annotations

Basic: TypeAlias = Annotated[
    sympy.Basic, TypeValidator(sympy.Basic), StrSerializer("json")
]
"""Annotated {class}`~sympy.core.basic.Basic` suitable for use in Pydantic models."""
Symbol: TypeAlias = Annotated[sympy.Symbol, TypeValidator(sympy.Symbol)]
"""Annotated {class}`~sympy.core.symbol.Symbol` suitable for use in Pydantic models."""
Eq: TypeAlias = Annotated[
    Basic, BeforeValidator(validate_expr), TypeValidator(sympy.Eq, "after")
]
"""{data}`~boilercv_pipeline.types.Basic` narrowed to {class}`~sympy.core.relational.Eq`."""
Expr: TypeAlias = Annotated[
    Basic, BeforeValidator(validate_expr), TypeValidator(sympy.Expr, "after")
]
"""{data}`~boilercv_pipeline.types.Basic` narrowed to {class}`~sympy.core.relational.Eq`."""
