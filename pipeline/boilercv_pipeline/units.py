"""Units."""

from pint import UnitRegistry

PX_PER_M = 20997.3753
U = UnitRegistry(auto_reduce_dimensions=True, system="SI")
U.define("@alias coulomb = Co")
U.define("@alias degC = C")
U.define(f"m = {PX_PER_M} * px")
Q = U.Quantity
