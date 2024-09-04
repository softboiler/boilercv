"""Units."""

from pint import UnitRegistry

U = UnitRegistry(auto_reduce_dimensions=True, system="SI")
U.define("@alias coulomb = Co")
U.define("@alias degC = C")
Q = U.Quantity
