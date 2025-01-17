"""Docs config."""

from datetime import date
from hashlib import sha256
from pathlib import Path

from boilercv_dev.docs.config import default
from boilercv_dev.docs.intersphinx import get_ispx, get_rtd, get_url
from boilercv_dev.docs.models.paths import rooted_paths
from boilercv_dev.docs.patch_notebooks import patch_notebooks
from boilercv_dev.docs.types import IspxMappingValue
from boilercv_dev.tools.environment import sync_environment_variables
from boilercv_dev.tools.warnings import filter_boilercv_warnings
from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from sphinx.application import Sphinx

# * MARK: Helper functions


def init_docs_build() -> Path:
    """Initialize shell, ensure we are in `docs`, patch notebooks, return root."""
    filter_boilercv_warnings()
    sync_environment_variables(rooted_paths.root)
    patch_notebooks()
    return rooted_paths.root


def dpaths(*paths: Path, rel: Path = rooted_paths.docs) -> list[str]:
    """Get the string-representation of paths relative to docs for Sphinx config.

    Parameters
    ----------
    paths
        Paths to convert.
    rel
        Relative path to convert to. Defaults to the 'docs' directory.
    """
    return [dpath(path, rel) for path in paths]


def dpath(path: Path, rel: Path = rooted_paths.docs) -> str:
    """Get the string-representation of a path relative to docs for Sphinx config.

    Parameters
    ----------
    path
        Path to convert.
    rel
        Relative path to convert to. Defaults to the 'docs' directory.
    """
    return path.relative_to(rel).as_posix()


# * MARK: Constants


class Answers(BaseModel, extra="ignore"):
    """Answers."""

    user: str = Field(alias="project_owner_github_username")
    """Name of the project owner."""
    repo: str = Field(alias="github_repo_name")
    """GitHub repository name."""
    package: str = Field(alias="project_name")
    """Package name."""
    version: str = Field(alias="project_version")
    """Package version."""


class Constants(BaseModel):
    """Constants."""

    root: Path = init_docs_build()
    """Root directory of the project."""
    static: Path = rooted_paths.docs / "_static"
    """Static assets folder, used in configs and setup."""
    css: Path = static / "local.css"
    """Local CSS file, used in configs and setup."""
    bib_template: Path = rooted_paths.docs / "refs-template.bib"
    """Project template bibliography file."""
    bib: Path = rooted_paths.docs / "refs.bib"
    """Bibliography file."""
    copier_answers: Path = root / ".copier-answers.yml"
    """Copier answers file."""
    authors: str = "Blake Naccarato, Kwang Jin Kim"
    """Authors of the project."""
    ans: Answers = Answers(**YAML().load(copier_answers.read_text(encoding="utf-8")))
    """Project template answers."""
    ispx_mapping: dict[str, IspxMappingValue] = {
        **{
            pkg: get_rtd(pkg)
            for pkg in [
                "cappa",
                "myst_parser",
                "nbformat",
                "numpydoc",
                "pint",
                "tomlkit",
                "typing_extensions",
            ]
        },
        **{pkg: get_rtd(pkg, latest=True) for pkg in ["pyqtgraph"]},
        "jupyterbook": get_url("jupyterbook.org/en"),
        "numpy": get_url("numpy.org/doc"),
        "matplotlib": get_url("matplotlib.org"),
        "pytest": get_url("docs.pytest.org/en"),
        "sympy": get_url("docs.sympy.org", latest=True),
        "colorcet": get_ispx("https://colorcet.holoviz.org"),
        "cv2": get_ispx("docs.opencv.org/2.4"),
        "pandas": get_ispx("pandas.pydata.org/docs"),
        "python": get_ispx("docs.python.org/3"),
        "scipy": get_ispx("docs.scipy.org/doc/scipy"),
        "boilercore": IspxMappingValue("https://softboiler.org/boilercore"),
        "context_models": IspxMappingValue("https://softboiler.org/context_models"),
    }
    """Intersphinx mapping."""
    tippy_rtd_urls: list[str] = [
        ispx.url
        for pkg, ispx in ispx_mapping.items()
        if pkg not in ["python", "pandas", "matplotlib"]
    ]
    """Tippy ReadTheDocs-compatible URLs."""
    rev: str = "88821fb2c86b83462115123dbd781d25a47cb51e"
    """Binder revision."""
    html_thebe_common: dict[str, str] = {
        "repository_url": f"https://github.com/{ans.user}/{ans.repo}",
        "path_to_docs": dpath(rooted_paths.docs),
    }
    """Options common to HTML and Thebe config."""


const = Constants()
"""Constants."""

# * MARK: Setup


def setup(app: Sphinx):
    """Add functions to Sphinx setup."""
    app.connect("html-page-context", add_version_to_css)


def add_version_to_css(app: Sphinx, _pagename, _templatename, ctx, _doctree):
    """Add the version number to the local.css file, to bust the cache for changes.

    See Also
    --------
    https://github.com/executablebooks/MyST-Parser/blob/978e845543b5bcb7af0ff89cac9f798cb8c16ab3/docs/conf.py#L241-L249
    """
    if app.builder.name != "html":
        return
    css = dpath(const.css)
    css_files = "css_files"
    for i, css_file in enumerate(ctx.get(css_files, [])):
        if css != css_file.filename:
            continue
        ctx[css_files][i] = f"{css}?hash={sha256(const.css.read_bytes()).hexdigest()}"


# * MARK: Basics


project = const.ans.package
copyright = f"{date.today().year}, {const.authors}"  # noqa: A001
version = const.ans.version
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**/_*.md", "**/_*.ipynb"]
extensions = [
    *([] if default.build.skip_autodoc else ["autodoc2", "cappa.ext.docutils"]),
    "myst_nb",
    "sphinx_design",
    "sphinx_tippy",
    "sphinx_thebe",
    "sphinx_togglebutton",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinxcontrib.bibtex",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.towncrier",
]
suppress_warnings = [
    "autodoc2.dup_item"  # "Duplicate items in boilercv_tests.test_morphs
]
# * MARK: Theme
html_title = project
html_favicon = "_static/favicon.ico"
html_logo = "_static/favicon.ico"
html_static_path = dpaths(const.static)
html_css_files = dpaths(const.css, rel=const.static)
html_theme = "sphinx_book_theme"
html_context = {
    # ? MyST elements don't look great with dark mode, but allow dark for accessibility.
    "default_mode": "light"
}
html_theme_options = {
    **const.html_thebe_common,
    "navigation_with_keys": False,  # https://github.com/pydata/pydata-sphinx-theme/pull/1503
    "repository_branch": "main",
    "show_navbar_depth": 2,
    "show_toc_level": 4,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "use_repository_button": True,
}
# * MARK: MyST
mathjax3_config = {
    "tex": {
        "macros": {
            # ? User-defined macros: https://docs.mathjax.org/en/latest/input/tex/macros.html
            # ? Built-in macros: https://docs.mathjax.org/en/latest/input/tex/macros/index.html#tex-commands
            **{
                const: rf"\mathit{{{const}}}"
                for const in ["Fo", "Ja", "Nu", "Pe", "Pr", "Re"]
            },
            **{f"{const}o": rf"\mathit{{{const}0}}" for const in ["", "b"]},
        }
    }
}
myst_enable_extensions = [
    "attrs_block",
    "colon_fence",
    "deflist",
    "dollarmath",
    "linkify",
    "strikethrough",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 6
myst_substitutions = {
    "binder": f"[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/{const.ans.user}/{project}/{const.rev}?labpath=docs%2Fnotebooks%2Ffind_objects.ipynb)"
}
# * MARK:  BibTeX
bibtex_bibfiles = dpaths(const.bib_template, const.bib)
bibtex_reference_style = "label"
bibtex_default_style = "unsrt"
# * MARK:  NB
nb_execution_mode = default.build.nb_execution_mode
nb_execution_excludepatterns = default.build.nb_execution_excludepatterns
nb_execution_raise_on_error = True
nb_execution_timeout = 120
nb_render_markdown_format = "myst"
# * MARK:  Thebe
thebe_config = {
    **const.html_thebe_common,
    "repository_branch": const.rev,
    "selector": "div.highlight",
}
# * MARK:  Other
numfig = True
math_eqref_format = "Eq. {number}"
mermaid_d3_zoom = False
# * MARK:  Autodoc2
nitpicky = True
autodoc2_packages = [
    f"../src/{project}",
    "../packages/_dev/boilercv_dev",
    f"../packages/pipeline/{project}_pipeline",
]
autodoc2_render_plugin = "myst"
# ? Autodoc2 does not currently obey `python_display_short_literal_types` or
# ? `python_use_unqualified_type_names`, but `maximum_signature_line_length` makes it a
# ? bit prettier.
# ? https://github.com/sphinx-extensions2/sphinx-autodoc2/issues/58
maximum_signature_line_length = 1
# ? Parse Numpy docstrings
if not default.build.skip_autodoc_post_parse:
    autodoc2_docstring_parser_regexes = [(".*", "boilercv_dev.docs.docstrings")]
# * MARK:  Intersphinx
intersphinx_mapping = {
    pkg: ispx for pkg, ispx in const.ispx_mapping.items() if pkg != "colorcet"
}
nitpick_ignore = [
    ("py:obj", "typing.Annotated"),
    ("py:class", "cv2.LineSegmentDetector"),
    ("py:class", "pandas.core.groupby.generic.DataFrameGroupBy"),
    ("py:class", f"{project}.correlations.T"),
    ("py:class", f"{project}.data.sets.Stage"),
    ("py:class", f"{project}.experiments.e230920_subcool.NbProcess"),
    ("py:class", f"{project}.experiments.e230920_subcool.NbProcess"),
    ("py:class", f"{project}.morphs.contexts"),
]
nitpick_ignore_regex = [
    # ? Auto-generated or otherwise too hard to separate into own `types` modules
    (r"py:.+", rf"{project}_pipeline\.models\.dvc\..+"),
    (r"py:.+", rf"{project}_pipeline\.models\.path\..+"),
    (r"py:.+", rf"{project}_pipeline\.models\.column\..+"),
    (r"py:.+", rf"{project}_pipeline\.stages\..+"),
    # ? Missing inventory
    (r"py:.+", r"cappa\..+"),
    (r"py:.+", r"docutils\..+"),
    (r"py:.+", r"numpydoc\.docscrape\..+"),
    (r"py:.+", r"_pytest\..+"),
    (r"py:.+", r"numpy\.typing\..+"),
    (r"py:.+", r"tomlkit\.container\..+"),
    (  # ? sympy: https://github.com/sympy/sympy/issues/17619#issuecomment-536781620
        r"py:.+",
        r"sympy\..+",
    ),
    (r"py:.+", r"pydantic\..+"),  # ? https://github.com/pydantic/pydantic/issues/1339
    (
        r"py:.+",
        r"pydantic_settings\..+",
    ),  # ? https://github.com/pydantic/pydantic/issues/1339
    (r"py:.+", r"PySide6\..+"),  # ? https://bugreports.qt.io/browse/PYSIDE-2215
    # ? TypeAlias: https://github.com/sphinx-doc/sphinx/issues/10785
    (r"py:.+", r"dev.*\.types\..+"),
    (r"py:.+", rf"{project}.*\.types\..+"),
    (r"py:.+", r"boilercore.*\.types\..+"),
    (r"py:.+", r"context_models.*\.types\..+"),
    (r"py:.+", rf"{project}_pipeline\.captivate\.previews\..+"),
]
# * MARK:  Tippy
# ? https://sphinx-tippy.readthedocs.io/en/latest/index.html#confval-tippy_anchor_parent_selector
tippy_anchor_parent_selector = "article.bd-article"
# ? Mermaid tips don't work
tippy_skip_anchor_classes = ["mermaid"]
# ? https://github.com/sphinx-extensions2/sphinx-tippy/issues/6#issuecomment-1627820276
tippy_enable_mathjax = True
tippy_tip_selector = """
    aside,
    div.admonition,
    div.literal-block-wrapper,
    figure,
    img,
    div.math,
    p,
    table
    """
# ? Skip Zenodo DOIs as the hover hint doesn't work properly
tippy_rtd_urls = const.tippy_rtd_urls
tippy_skip_urls = [
    # ? Skip Zenodo DOIs as the hover hint doesn't work properly
    r"https://doi\.org/10\.5281/zenodo\..+"
]
# * MARK:  Towncrier
towncrier_draft_autoversion_mode = "draft"
towncrier_draft_include_empty = True
towncrier_draft_working_directory = const.root
towncrier_draft_config_path = rooted_paths.pyproject
