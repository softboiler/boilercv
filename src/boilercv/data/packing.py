"""Packing and unpacking of binarized video data."""

from numpy import packbits, unpackbits
from xarray import apply_ufunc

from boilercv.data import (
    DIMS,
    PACKED,
    PACKED_DIM_INDEX,
    PACKED_DIMS,
    VIDEO,
    XPX,
    XPX_PACKED,
)
from boilercv.types import DA


def pack(da: DA) -> DA:
    """Pack the bits in dimension of the data array."""
    return (
        apply_ufunc(
            packbits,
            da,
            kwargs=dict(axis=PACKED_DIM_INDEX),
            input_core_dims=[DIMS],
            output_core_dims=[DIMS],
            exclude_dims={XPX},
            keep_attrs=True,
        )
        .rename({XPX: XPX_PACKED})
        .assign_coords({XPX_PACKED: lambda da: da[XPX_PACKED].values})
        .rename(f"{VIDEO}_{PACKED}")
    )


def unpack(da: DA) -> DA:
    """Unpack the bits of the last image dimension of a data array."""
    return (
        apply_ufunc(
            unpackbits,
            da,
            kwargs=dict(axis=PACKED_DIM_INDEX),
            input_core_dims=[PACKED_DIMS],
            output_core_dims=[PACKED_DIMS],
            exclude_dims={XPX_PACKED},
            keep_attrs=True,
        )
        .rename({XPX_PACKED: XPX})
        .assign_coords({XPX: lambda da: da[XPX].values})
        .rename(VIDEO)
        .astype(bool)
    )
