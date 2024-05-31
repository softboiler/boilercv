"""Update expected results for the response of each correlation to `KWDS`."""

from decimal import Decimal
from inspect import Signature, getmembers, isfunction

from tomlkit import dumps, parse

from boilercv.mappings import sort_by_keys_pattern
from boilercv_pipeline.correlations import dimensionless_bubble_diameter
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    EXPECTATIONS_TOML,
    SYMBOL_EXPECTATIONS,
)
from boilercv_pipeline.correlations.types.runtime import KeysPattern
from boilercv_pipeline.equations import equation_name_pattern, keys_pattern
from boilercv_pipeline.types.runtime import contextualized


def main():  # noqa: D103
    expectations = parse(EXPECTATIONS_TOML.read_text("utf-8"))
    symbols = {
        "Fo_0": "bubble_fourier",
        "Ja": "bubble_jakob",
        "Re_b0": "bubble_initial_reynolds",
        "Pr": "liquid_prandtl",
        "beta": "dimensionless_bubble_diameter",
        "pi": "pi",
    }
    for name, correlation in [
        (name, attr)
        for name, attr in getmembers(dimensionless_bubble_diameter)
        if isfunction(attr) and equation_name_pattern.match(name)
    ]:
        expectations[name] = [
            str(Decimal(r).quantize(Decimal(10) ** -6))
            for r in correlation(**{
                symbols[kwd]: value
                for kwd, value in SYMBOL_EXPECTATIONS.items()
                if symbols[kwd] in Signature.from_callable(correlation).parameters
            })
        ]
    EXPECTATIONS_TOML.write_text(
        encoding="utf-8",
        data=dumps(
            contextualized(KeysPattern)(sort_by_keys_pattern)(
                expectations, keys_pattern
            )
        ).replace('"', ""),
    )


if __name__ == "__main__":
    main()
