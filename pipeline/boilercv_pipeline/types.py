"""Types."""

from collections import UserDict
from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated, Any, Generic, Literal, NamedTuple, TypeAlias, TypeVar

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
from pydantic.alias_generators import to_snake
from pydantic_core.core_schema import NoInfoValidatorFunction, WithInfoValidatorFunction
from sympy import sympify

T = TypeVar("T")
K = TypeVar("K")
SK = TypeVar("SK")
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


class CtxV:
    """Context value."""

    @classmethod
    def name_to_snake(cls) -> str:
        """Get name."""
        return to_snake(cls.__name__)


Ctx: TypeAlias = dict[str, CtxV]


CtxV_T = TypeVar("CtxV_T", bound=CtxV)

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


class LocalSymbols(UserDict[SK, Symbol], CtxV, Generic[SK]):
    """Local symbols."""


@dataclass
class SympifyParams(CtxV, Generic[SK]):
    """Sympify parameters."""

    locals: dict[SK, Any] | None = None
    convert_xor: bool | None = None
    strict: bool = False
    rational: bool = False
    evaluate: bool | None = None


ValidatorF: TypeAlias = NoInfoValidatorFunction | WithInfoValidatorFunction


def contextualize(ctx_v_type: type[CtxV_T]):
    """Contextualize a function."""

    def wrapper(f):
        def validator(v: Callable[[str, CtxV_T], Any], info: ValidationInfo):
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


@contextualize(SympifyParams)
def validate_expr(expr: str, sympify_params: SympifyParams[Any]) -> Any:
    """Sympify an expression from local variables."""
    return sympify(expr, **asdict(sympify_params))


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


@dataclass
class Defaults(CtxV, Generic[K, V]):
    """Context for expression validation."""

    default_keys: tuple[K, ...] = field(default_factory=tuple)
    """Default keys."""
    default: V | None = None
    """Default value."""
    default_factory: Callable[..., Any] | None = None
    """Default value factory."""


class Pipe(NamedTuple):
    """Pipe."""

    morph: Callable[[Any, Any], Any]
    ctx_v: CtxV


class Morphs(dict[type, list[Pipe]], CtxV):
    """Morphs."""
