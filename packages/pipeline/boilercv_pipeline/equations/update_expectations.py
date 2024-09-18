"""Update expected results for the response of each correlation to `KWDS`."""

from inspect import Signature, getmembers, isfunction
from tomllib import loads
from typing import cast

from context_models.mappings import sync
from cyclopts import App
from tomlkit import TOMLDocument, parse
from tqdm import tqdm

from boilercv.correlations import SYMBOLS, beta
from boilercv.correlations.models import Expectations
from boilercv.correlations.pipes import equation_name_pattern
from boilercv.correlations.types import Corr
from boilercv_pipeline.equations import EXPECTATIONS, SUBSTITUTIONS

default_substitutions = cast(
    tuple[tuple[str, float], ...], tuple(beta.SYMBOL_EXPECTATIONS.items())
)

TIMEOUT = 5
"""Solver timeout in seconds."""
APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def default(corr: Corr = "beta", overwrite: bool = False):  # noqa: D103
    expectations = EXPECTATIONS[corr]
    substitutions = SUBSTITUTIONS[corr]

    content = expectations.read_text("utf-8") if expectations.exists() else ""
    expec = Expectations[str](loads(content))
    for name, correlation in tqdm([
        (name, attr)
        for name, attr in getmembers(beta)
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
