"""Preview a single video."""

from cyclopts import App

from boilercv.correlations.types import Stage
from boilercv_pipeline.captivate.previews import view_images
from boilercv_pipeline.sets import get_dataset

APP = App()
"""CLI."""


def main():  # noqa: D103
    APP()


@APP.default
def preview_single(name: str, stage: Stage = "large_sources"):
    """Preview a single dataset."""
    view_images(get_dataset(name=name, stage=stage)["video"])


if __name__ == "__main__":
    main()
