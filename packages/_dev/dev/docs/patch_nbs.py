"""Patch notebooks."""

from copy import deepcopy
from textwrap import dedent

from nbformat import NO_CONVERT, NotebookNode, read, write

from dev.docs.models.paths import rooted_paths

EXCLUDE_THEBE = ["find_tracks", "find_tracks_trackpy"]
"""Resourcse-intensive notebooks to exclude adding Thebe buttons to."""
SRC = "source"
"""Cell source key."""
CODE = "code"
"""Code cell type."""
MD = "markdown"
"""Markdown cell type."""


def patch_nbs():
    """Patch notebooks.

    Patch Thebe buttons in. Insert `parameters` and `thebe-init` tags to the first code
    cell. Insert `hide-input` tags to code cells.
    """
    for path in rooted_paths.notebooks.iterdir():
        orig_nb: NotebookNode = read(path, NO_CONVERT)  # pyright: ignore[reportAssignmentType]
        nb = deepcopy(orig_nb)
        if path.stem not in EXCLUDE_THEBE:
            # ? Patch the first Markdown cell
            i, first = next((i, c) for i, c in enumerate(nb.cells) if c.cell_type == MD)
            nb.cells[i][SRC] = patch(
                first.get(SRC, ""),
                """
                ::::
                :::{thebe-button}
                :::
                ::::
                """,
            )
        code_cells = ((i, c) for i, c in enumerate(nb.cells) if c.cell_type == CODE)
        # ? Insert tags to first code cell
        i, first = next(code_cells)
        nb.cells[i] = insert_tag(
            first,
            [
                "hide-input",
                "parameters",
                *([] if path.stem in EXCLUDE_THEBE else ["thebe-init"]),
            ],
        )
        # ? Insert tags to remaining code cells
        for i, cell in code_cells:
            nb.cells[i] = insert_tag(cell, ["hide-input"])
        # ? Write the notebook back
        if nb != orig_nb:
            write(nb, path)


def insert_tag(cell: NotebookNode, tags_to_insert: list[str]) -> NotebookNode:
    """Insert tags to a notebook cell.

    Parameters
    ----------
    cell
        Notebook cell to insert tags to.
    tags_to_insert
        Tags to insert.

    References
    ----------
    - [Jupyter Book: Add tags using Python code](https://jupyterbook.org/en/stable/content/metadata.html#add-tags-using-python-code)
    """
    tags = cell.get("metadata", {}).get("tags", [])
    cell["metadata"]["tags"] = sorted(set(tags) | set(tags_to_insert))
    return cell


def patch(src: str, content: str, end: str = "\n\n") -> str:
    """Prepend source lines to cell source if not there already.

    Parameters
    ----------
    src
        Source to prepend to.
    content
        Content to prepend.
    end
        Ending to append to the content.
    """
    content = dedent(content).strip()
    return src if src.startswith(content) else f"{content}{end}{src}"


if __name__ == "__main__":
    patch_nbs()
