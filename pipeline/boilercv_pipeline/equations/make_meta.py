"""Make empty meta file."""

from cyclopts import App
from tomlkit import TOMLDocument, parse

from boilercv.correlations import META_TOML
from boilercv.correlations.models import Metadata
from boilercv.mappings import sync

APP = App()
"""CLI."""


def main():  # noqa: D103
    META_TOML.write_text(
        encoding="utf-8",
        data=sync(
            reference=Metadata.context_model_validate(
                obj=parse(META_TOML.read_text("utf-8") if META_TOML.exists() else ""),
                context=Metadata.get_context(),
            ).model_dump(mode="json"),
            target=TOMLDocument(),
        ).as_string(),
    )


if __name__ == "__main__":
    main()
