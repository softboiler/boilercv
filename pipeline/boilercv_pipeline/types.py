"""Types."""

from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import asdict, dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import (
    Annotated,
    Any,
    Generic,
    Literal,
    NamedTuple,
    Protocol,
    TypeAlias,
    TypeVar,
)

import sympy
from numpydantic import NDArray, Shape
from numpydantic.types import DtypeType, ShapeType
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    PlainSerializer,
    PlainValidator,
    ValidationInfo,
    WrapValidator,
)
from sympy import sympify
from typing_extensions import TypedDict

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# * MARK: Notebook processing

NbProcess: TypeAlias = Callable[[Path, SimpleNamespace], None]
"""Notebook process."""
Stage: TypeAlias = Literal["large_sources", "sources", "filled"]
"""Stage."""

# * MARK: Pydantic helpers

Validators: TypeAlias = Literal["before", "wrap", "after", "plain"]

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


ST = TypeVar("ST", bound=ShapeType)
DT = TypeVar("DT", bound=DtypeType)

# * MARK: Morphs


class Repl(NamedTuple, Generic[T]):
    """Contents of `dst` to replace with `src`, with `find` substrings replaced with `repl`."""

    src: T
    """Source identifier."""
    dst: T
    """Destination identifier."""
    find: str
    """Find this in the source."""
    repl: str
    """Replacement for what was found."""


AnyShape: TypeAlias = Shape["*"]  # noqa: F722
"""Any shape."""
Vector: TypeAlias = Shape["*"]  # noqa: F722
"""Vector shape."""
Expectation: TypeAlias = float | NDArray[Vector, float]  # pyright: ignore[reportInvalidTypeArguments]
"""Expectation."""
Leaf: TypeAlias = Any
"""Leaf node."""
Node: TypeAlias = Mapping[Any, "Node | Leaf"]
"""General node."""
MutableNode: TypeAlias = MutableMapping[Any, "MutableNode | Leaf"]
"""Mutable general node."""
Basic: TypeAlias = Annotated[
    sympy.Basic, TypeValidator(sympy.Basic), StrSerializer("json")
]
"""Annotated {class}`~sympy.core.basic.Basic` suitable for use in Pydantic models."""
Symbol: TypeAlias = Annotated[sympy.Symbol, TypeValidator(sympy.Symbol)]
"""Annotated {class}`~sympy.core.symbol.Symbol` suitable for use in Pydantic models."""
LocalSymbols: TypeAlias = dict[str, Symbol]
"""Local symbols."""


@dataclass
class SympifyParams:
    """Sympify parameters."""

    locals: LocalSymbols | None = None
    convert_xor: bool | None = None
    strict: bool = False
    rational: bool = False
    evaluate: bool | None = None


class ExprContext(TypedDict):
    """Context for expression validation."""

    params: SympifyParams
    """Sympify parameters."""


class ExprValidationInfo(ValidationInfo, Protocol):
    """Argument passed to validation functions."""

    @property
    def context(self) -> ExprContext | None:
        """Current validation context."""


def validate_expr(expr: str, info: ExprValidationInfo):
    """Sympify an expression from local variables."""
    return sympify(
        expr, **asdict(ctx["params"] if (ctx := info.context) else SympifyParams())
    )


Eq: TypeAlias = Annotated[
    Basic, BeforeValidator(validate_expr), TypeValidator(sympy.Eq, "after")
]
"""{data}`~boilercv_pipeline.boilercv_pipeline.Basic` narrowed to {class}`~sympy.core.relational.Eq`."""


Expr = Annotated[
    Basic, BeforeValidator(validate_expr), TypeValidator(sympy.Expr, "after")
]
"""{data}`~boilercv_pipeline.boilercv_pipeline.Basic` narrowed to {class}`~sympy.core.relational.Eq`."""


Model = TypeVar("Model", bound=BaseModel)
"""Model type."""

Context = TypeVar("Context", contravariant=True)
"""Context mapping type."""


class ContextualValidation(Protocol[Context]):
    """Validation type-checking for {data}`~boilercv_pipeline.boilercv_pipeline.Expr`."""

    @classmethod
    def model_validate(  # pyright: ignore[reportIncompatibleMethodOverride]  # noqa: D102
        cls: type[Model],
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Context | None = None,
    ) -> Model: ...

    @classmethod
    def model_validate_json(  # pyright: ignore[reportIncompatibleMethodOverride]  # noqa: D102
        cls: type[Model],
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: Context | None = None,
    ) -> Model: ...
