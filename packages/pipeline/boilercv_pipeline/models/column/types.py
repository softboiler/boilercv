"""Types."""

from typing import TYPE_CHECKING, ParamSpec, Protocol, TypeVar

from boilercv.types import SupportsMul

if TYPE_CHECKING:
    from boilercv_pipeline.models.column import Col

SupportsMul_T = TypeVar("SupportsMul_T", bound=SupportsMul)
"""Type that supports multiplication."""
P = TypeVar("P", contravariant=True)
"""Contravariant type to represent parameters."""
R = TypeVar("R", covariant=True)
"""Covariant type to represent returns."""
Ps = ParamSpec("Ps")
"""Parameter type specification."""


class Transform(Protocol[P, R, Ps]):
    def __call__(
        self, v: P, src: "Col", dst: "Col", /, *args: Ps.args, **kwds: Ps.kwargs
    ) -> R: ...
