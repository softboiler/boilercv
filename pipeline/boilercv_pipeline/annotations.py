"""Pydantic annotations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Annotated, Any, Generic, Literal, TypeAlias, TypeVar

import sympy
from pydantic import (
    AfterValidator,
    BeforeValidator,
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
    WrapValidator,
)
from pydantic.alias_generators import to_snake
from sympy import sympify

# * MARK: `TypeVar`s and `TypeAlias`es for annotations

K = TypeVar("K")
CV = TypeVar("CV", bound="CtxV", contravariant=True)

SK = TypeVar("SK")
"""Symbol key."""

Validators: TypeAlias = Literal["before", "wrap", "after", "plain"]
"""Validators."""

# * MARK: Needed for annotations and other things


class CtxV:
    """Context value."""

    @classmethod
    def name_to_snake(cls) -> str:
        """Get name."""
        return to_snake(cls.__name__)


# * MARK: Annotation parts


def contextualize(ctx_v_type: type[CV]):
    """Contextualize a function."""

    def wrapper(f):
        def validator(v: Callable[[str, CV], Any], info: ValidationInfo):
            key = ctx_v_type.name_to_snake()
            ctx = info.context
            if not ctx:
                raise ValueError(
                    f"No context given. Expected value at '{key}' of type '{ctx_v_type}'."
                )
            ctx_v = ctx.get(key)
            if not ctx_v:
                raise ValueError(
                    f"No context value at {key}. Expected context value at '{key}' of type '{ctx_v_type}'."
                )
            if not isinstance(ctx_v, ctx_v_type):
                raise ValueError(  # noqa: TRY004. So Pydantic continues
                    f"Context value at {key} not of expected type '{ctx_v_type}'."
                )
            return f(v, ctx_v)

        return validator

    return wrapper


@dataclass
class SympifyParams(CtxV, Generic[SK]):
    """Sympify parameters."""

    locals: dict[SK, Any] | None = None
    convert_xor: bool | None = None
    strict: bool = False
    rational: bool = False
    evaluate: bool | None = None


@contextualize(SympifyParams)
def validate_expr(expr: str, sympify_params: SympifyParams[Any]) -> Any:
    """Sympify an expression from local variables."""
    return sympify(expr, **asdict(sympify_params))


VALIDATORS: dict[Validators, Any] = {
    "before": BeforeValidator,
    "wrap": WrapValidator,
    "after": AfterValidator,
    "plain": PlainValidator,
}
"""Validators."""


def TypeValidator(typ: type[K], mode: Validators = "plain") -> PlainValidator:  # noqa: N802; Can't inherit from frozen
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
"""{data}`~boilercv_pipeline.boilercv_pipeline.Basic` narrowed to {class}`~sympy.core.relational.Eq`."""
Expr: TypeAlias = Annotated[
    Basic, BeforeValidator(validate_expr), TypeValidator(sympy.Expr, "after")
]
"""{data}`~boilercv_pipeline.boilercv_pipeline.Basic` narrowed to {class}`~sympy.core.relational.Eq`."""
