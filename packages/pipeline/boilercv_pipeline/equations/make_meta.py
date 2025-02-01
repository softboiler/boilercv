"""Make empty meta file."""

from context_models.mappings import sync
from cyclopts import App
from tomlkit import TOMLDocument, parse

from boilercv.correlations import META_TOML
from boilercv.correlations.models import Metadata
from boilercv.pipelines.contexts import get_pipeline_context

APP = App()
"""CLI."""


def main():
    META_TOML.write_text(
        encoding="utf-8",
        data=sync(
            reference=Metadata.model_validate(
                obj=parse(META_TOML.read_text("utf-8") if META_TOML.exists() else ""),
                context=get_pipeline_context(Metadata.get_context()),
            ).model_dump(mode="json"),
            target=TOMLDocument(),
        ).as_string(),
    )


if __name__ == "__main__":
    main()
