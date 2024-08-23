"""Documentation utilities."""

from collections.abc import Callable
from contextlib import contextmanager, nullcontext, redirect_stdout
from io import StringIO
from os import environ, remove
from pathlib import Path
from re import match, search, sub
from shutil import copytree
from tempfile import NamedTemporaryFile
from textwrap import dedent
from typing import Any
from warnings import catch_warnings, filterwarnings

from IPython.display import HTML, display
from IPython.utils.capture import capture_output
from myst_parser.parsers.docutils_ import cli_html
from pandas import DataFrame, Index, MultiIndex, Series, concat, options

from boilercv_docs.config import default
from boilercv_docs.models.paths import rooted_paths
from boilercv_docs.types import BuildMode, DfOrS
from boilercv_pipeline.models.types.runtime import (
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


# * -------------------------------------------------------------------------------- * #
# * Render Math in DataFrames locally and in generated docs
# * https://github.com/executablebooks/jupyter-book/issues/1501#issuecomment-1721378476


def display_dataframe_with_math(df, raw=False):
    """Display a dataframe with MathJax-rendered math."""
    html = df.to_html()
    raw_html = sub(r"\$.*?\$", lambda m: convert_tex_to_html(m[0], raw=True), html)  # pyright: ignore[reportArgumentType, reportCallIssue]
    return raw_html if raw else HTML(raw_html)


def convert_tex_to_html(html, raw=False):
    """Manually apply the MyST parser to convert $-$ into MathJax's HTML code."""
    frontmatter = """
    ---
    myst:
      enable_extensions: [dollarmath, amsmath]
    ---
    """
    with NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
        f.write(dedent(frontmatter).strip())
        f.write("\n\n")
        f.write(html)
    with redirect_stdout(StringIO()) as sf:
        cli_html([f.name])
    fullhtml = sf.getvalue()  # Returns a large-ish HTML with the full styling header
    remove(f.name)  # noqa: PTH107
    # Strip HTML headers to keep only the body with converted math
    m = search(r'<body>\n<div class="document">([\s\S]*)</div>\n</body>', fullhtml)
    raw_html = m[1].strip()  # pyright: ignore[reportOptionalSubscript]
    # Special case: if we provided a snippet with no HTML markup at all, don't wrap the result
    # in <p> tags
    if "\n" not in html and "<" not in html and (m := match(r"<p>(.*)</p>", raw_html)):
        raw_html = m[1]
    # Manually display the result as HTML
    return raw_html if raw else HTML(raw_html)


# * -------------------------------------------------------------------------------- * #
# * Make styled dataframes respect precision
# * https://gist.github.com/blakeNaccarato/3c751f0a9f0f5143f3cffc525e5dd577


@contextmanager
def style_df(df: DfOrS, head: bool = False):
    """Style a dataframe."""
    df, truncated = truncate(df, head)
    styler = df.style
    yield styler
    display(styler.format(get_df_formatter(df, truncated)))  # pyright: ignore[reportArgumentType]  # pyright 1.1.333


def display_dfs(*dfs: DfOrS, head: bool = False):
    """Display formatted DataFrames.

    When a mapping of column names to callables is given to the Pandas styler, the
    callable will be used internally by Pandas to produce formatted strings. This
    differs from elementwise formatting, in which Pandas expects the callable to
    actually process the value and return the formatted string.
    """
    for df in dfs:
        df, truncated = truncate(df, head)
        display(df.style.format(get_df_formatter(df, truncated)))  # pyright: ignore[reportArgumentType]  # pyright 1.1.333


def get_df_formatter(
    df: DataFrame, truncated: bool, precision: int = 4
) -> Callable[..., str] | dict[str, Callable[..., str]]:
    """Get formatter for the dataframe."""
    if truncated:
        return format_cell
    cols = df.columns
    types = {col: dtype.type for col, dtype in zip(cols, df.dtypes, strict=True)}
    return {col: get_formatter(types[col](), precision=precision) for col in cols}


def format_cell(cell, precision: int = 4) -> str:
    """Format individual cells."""
    return get_formatter(cell, precision=precision)(cell)


def get_formatter(instance: Any, precision: int) -> Callable[..., str]:
    """Get the formatter depending on the type of the instance."""
    float_spec = f"#.{precision}g"
    match instance:
        case float():
            return lambda cell: f"{cell:{float_spec}}"
        case _:
            return lambda cell: f"{cell}"


def truncate(df: DfOrS, head: bool = False) -> tuple[DataFrame, bool]:
    """Truncate long dataframes, showing only the head and tail."""
    if isinstance(df, Series):
        df = df.to_frame()
    if len(df) <= options.display.max_rows:
        return df, False
    if head:
        return df.head(options.display.min_rows), True
    df = df.copy()
    # Resolves case when column names are not strings for latter assignment, e.g. when
    # the column axis is a RangeIndex.
    df.columns = [str(col) for col in df.columns]
    # Resolves ValueError: Length of names must match number of levels in MultiIndex.
    ellipsis_index = ("...",) * df.index.nlevels
    df = concat([
        df.head(options.display.min_rows // 2),
        df.iloc[[0]]  # Resolves ValueError: cannot handle a non-unique multi-index!
        .reindex(
            MultiIndex.from_tuples([ellipsis_index], names=df.index.names)
            if isinstance(df.index, MultiIndex)
            else Index(ellipsis_index, name=df.index.name)
        )
        .assign(**dict.fromkeys(df.columns, "...")),
        df.tail(options.display.min_rows // 2),
    ])
    return df, True
