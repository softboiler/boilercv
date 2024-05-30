"""Update expected results for the response of each correlation to `KWDS`."""

from decimal import Decimal
from inspect import Signature, getmembers, isfunction

from tomlkit import dumps, parse

from boilercv_pipeline.correlations import _beta
from boilercv_pipeline.correlations.dimensionless_bubble_diameter import (
    EXPECTATIONS_TOML,
    KWDS,
)


def main():  # noqa: D103
    expectations = parse(EXPECTATIONS_TOML.read_text("utf-8"))
    for name, correlation in [
        (name, attr) for name, attr in getmembers(_beta) if isfunction(attr)
    ]:
        foo = correlation(**{  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
            kwd: value
            for kwd, value in KWDS.items()
            if kwd in Signature.from_callable(correlation).parameters
        })
        expectations[name] = [str(Decimal(r).quantize(Decimal(10) ** -6)) for r in foo]
    EXPECTATIONS_TOML.write_text(
        encoding="utf-8", data=dumps(expectations).replace('"', "")
    )


if __name__ == "__main__":
    main()
