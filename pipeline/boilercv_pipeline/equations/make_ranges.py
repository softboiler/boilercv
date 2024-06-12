"""Make empty ranges file."""

from cyclopts import App
from tomlkit import parse

from boilercv.correlations import RANGES_TOML
from boilercv.correlations.models import Equations
from boilercv.mappings import sync
from boilercv_pipeline.equations import SYMS, get_raw_equations_context, make_raw

APP = App()
"""CLI."""


def main():  # noqa: D103
    RANGES_TOML.write_text(
        encoding="utf-8",
        data=make_raw(
            sync(
                reference=Equations[str]
                .context_model_validate(
                    obj=(
                        content := parse(
                            RANGES_TOML.read_text("utf-8")
                            if RANGES_TOML.exists()
                            else ""
                        )
                    ),
                    context=get_raw_equations_context(symbols=SYMS),
                )
                .model_dump(mode="json"),
                target=content,
            ).as_string()
        ),
    )


if __name__ == "__main__":
    main()
