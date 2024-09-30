"""Documentation utilities."""

from contextlib import contextmanager, nullcontext
from os import environ
from pathlib import Path
from shutil import copytree
from warnings import catch_warnings, filterwarnings

from boilercv_pipeline.models.contexts import BoilercvPipelineContexts, Roots
from boilercv_pipeline.models.path import get_boilercv_pipeline_context
from IPython.utils.capture import capture_output

from dev.docs.config import default
from dev.docs.models.paths import rooted_paths
from dev.docs.types import BuildMode
from dev.tools.warnings import filter_boilercv_warnings


def init(mode: BuildMode | None = None) -> BoilercvPipelineContexts:
    """Initialize a documentation notebook."""
    # sourcery skip: extract-method, remove-pass-elif
    filter_boilercv_warnings()
    mode = mode or default.build.force_mode or get_mode()
    if _in_binder := environ.get("BINDER_LAUNCH_HOST"):
        copytree(rooted_paths.docs_data, rooted_paths.pipeline_data, dirs_exist_ok=True)
    if mode == "docs" or (_in_ci := environ.get("CI")):
        return get_boilercv_pipeline_context(
            roots=Roots(data=rooted_paths.docs_data, docs=rooted_paths.docs)
        )
    return get_boilercv_pipeline_context(
        roots=Roots(data=rooted_paths.pipeline_data, docs=rooted_paths.docs)
    )


def get_mode() -> BuildMode:
    """Get notebook mode."""
    return default.build.force_mode or (
        "dev" if (Path().cwd() == rooted_paths.root) else "docs"
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
