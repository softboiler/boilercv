"""Documentation utilities."""

from contextlib import contextmanager, nullcontext
from os import environ
from pathlib import Path
from shutil import copytree
from warnings import catch_warnings, filterwarnings

from IPython.display import Markdown, display
from IPython.utils.capture import capture_output
from pandas import DataFrame

from boilercv_docs.config import default
from boilercv_docs.models.paths import rooted_paths
from boilercv_docs.types import BuildMode
from boilercv_pipeline.models.path import (
    BoilercvPipelineCtxDict,
    Roots,
    get_boilercv_pipeline_context,
)
from boilercv_tools.warnings import filter_boilercv_warnings


def init(force_mode: BuildMode = default.build.mode) -> BoilercvPipelineCtxDict:
    """Initialize a documentation notebook."""
    # sourcery skip: extract-method, remove-pass-elif
    filter_boilercv_warnings()
    at_root = Path().cwd() == rooted_paths.root
    if _in_binder := environ.get("BINDER_LAUNCH_HOST"):
        copytree(rooted_paths.docs_data, rooted_paths.pipeline_data, dirs_exist_ok=True)
    if force_mode == "docs" or (
        force_mode != "dev"
        and ((_in_docs := not at_root) or (_in_ci := environ.get("CI")))
    ):
        return get_boilercv_pipeline_context(
            roots=Roots(data=rooted_paths.docs_data, docs=rooted_paths.docs)
        )
    return get_boilercv_pipeline_context(
        roots=Roots(data=rooted_paths.pipeline_data, docs=rooted_paths.docs)
    )


@contextmanager
def nowarn(capture: bool = False):
    """Don't raise any warnings. Optionally capture output for pesky warnings."""
    with catch_warnings(), capture_output() if capture else nullcontext():
        filterwarnings("ignore")
        yield


def keep_viewer_in_scope():
    """Keep the image viewer in scope so it doesn't get garbage collected."""
    from boilercv_pipeline.captivate.previews import image_viewer  # noqa: PLC0415

    with image_viewer([]) as viewer:
        return viewer


def display_markdown(df: DataFrame, floatfmt: str = "#.3g"):
    """Render dataframes as Markdown, facilitating MathJax rendering.

    Notes
    -----
    https://github.com/jupyter-book/jupyter-book/issues/1501#issuecomment-2301641068
    """
    display(Markdown(df.to_markdown(floatfmt=floatfmt)))
