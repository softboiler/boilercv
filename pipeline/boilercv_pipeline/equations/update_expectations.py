"""Update expected results for the response of each correlation to `KWDS`."""

from inspect import Signature, getmembers, isfunction
from pathlib import Path
from tomllib import loads
from typing import cast

from cyclopts import App
from tomlkit import TOMLDocument, parse
from tqdm import tqdm

from boilercv.mappings import sync
from boilercv_pipeline.correlations import dimensionless_bubble_diameter
from boilercv_pipeline.correlations.models import Expectations
from boilercv_pipeline.correlations.pipes import equation_name_pattern
from boilercv_pipeline.equations import default_expectations
from boilercv_tests.test_equations.test_dimensionless_bubble_diameter import SYMBOLS

default_substitutions = cast(
    tuple[tuple[str, float], ...],
    tuple(dimensionless_bubble_diameter.SYMBOL_EXPECTATIONS.items()),
)

TIMEOUT = 5
"""Solver timeout in seconds."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(  # noqa: D103
    expectations: Path = default_expectations,
    substitutions: tuple[tuple[str, float], ...] = default_substitutions,
    overwrite: bool = False,
):
    content = expectations.read_text("utf-8") if expectations.exists() else ""
    expec = Expectations[str](loads(content))
    for name, correlation in tqdm([
        (name, attr)
        for name, attr in getmembers(dimensionless_bubble_diameter)
        if isfunction(attr) and equation_name_pattern.match(name)
    ]):
        if not overwrite and expec.get(name) is not None:
            continue
        expec[name] = correlation(**{
            SYMBOLS[kwd]: value
            for kwd, value in substitutions
            if SYMBOLS[kwd] in Signature.from_callable(correlation).parameters
        })
    expectations.write_text(
        encoding="utf-8",
        data=(
            sync(
                reference=expec.model_dump(mode="json"),
                target=TOMLDocument() if overwrite else parse(content),
            )
        ).as_string(),
    )


if __name__ == "__main__":
    main()
