"""Types."""

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated, Any, Generic, Literal, NamedTuple, TypeAlias, TypeVar

from numpy import float64
from numpydantic import NDArray, Shape
from numpydantic.types import DtypeType, ShapeType
from pydantic import PlainSerializer, PlainValidator
from sympy import Basic

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# * MARK: Notebook processing

NbProcess: TypeAlias = Callable[[Path, SimpleNamespace], None]
"""Notebook process."""
Stage: TypeAlias = Literal["large_sources", "sources", "filled"]
"""Stage."""

# * MARK: Pydantic helpers


def TypeValidator(typ: type[K]) -> PlainValidator:  # noqa: N802; Can't inherit from frozen
    """Validate type."""

    def validate(v: K) -> K:
        if isinstance(v, typ):
            return v
        raise ValueError(f"Input should be a valid {typ}")

    return PlainValidator(validate)


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


AnyShape: TypeAlias = Shape["*, ..."]  # noqa: F722
"""Any shape."""
Expectation: TypeAlias = NDArray[AnyShape, float64]  # pyright: ignore[reportInvalidTypeArguments]
"""Expectation."""
Leaf: TypeAlias = Any
"""Leaf node."""
Node: TypeAlias = dict[Any, "Node | Leaf"]
"""General node."""
Expr: TypeAlias = Annotated[Basic, TypeValidator(Basic), StrSerializer("json")]
"""Expression."""
