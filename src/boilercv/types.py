"""Types relevant to array manipulation and image processing."""

from typing import Any, Protocol, TypeAlias, TypeVar

from numpy import (
    bool_,
    datetime64,
    floating,
    generic,
    integer,
    number,
    timedelta64,
    typing,
)
from numpy.typing import NBitBase, NDArray
from pandas import DataFrame
from xarray import DataArray, Dataset

DA: TypeAlias = DataArray
DF: TypeAlias = DataFrame
DS: TypeAlias = Dataset

ArrayLike: TypeAlias = typing.ArrayLike
"""Array-like."""

Arr: TypeAlias = NDArray[generic]
"""Generic array type. Consistent with OpenCV's type annotations."""
ArrBool: TypeAlias = NDArray[bool_]
"""A boolean array."""
ArrFloat: TypeAlias = NDArray[floating[NBitBase]]
"""An integer array with arbitrary bit depth."""
ArrInt: TypeAlias = NDArray[integer[NBitBase]]
"""An integer array."""
ArrNum: TypeAlias = NDArray[number[NBitBase]]
"""A number array."""
ArrDT: TypeAlias = NDArray[datetime64]
"""Datetime array type."""
ArrTD: TypeAlias = NDArray[timedelta64]
"""Timedelta array type."""

Img: TypeAlias = ArrInt
"""An integer array representing an image."""
ImgBool: TypeAlias = ArrBool
"""A boolean array representing an image mask."""
ImgLike: TypeAlias = ArrayLike
"""An array-like object representable as an image."""

Vid: TypeAlias = Img
"""An integer array representing a video."""
VidBool: TypeAlias = ImgBool
"""A boolean array representing a video mask."""


class SupportsMul(Protocol):
    """Protocol for types that support multiplication."""

    def __mul__(self, other: Any) -> Any: ...


DA_T = TypeVar("DA_T", bound=DA)
