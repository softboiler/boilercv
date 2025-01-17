"""Types."""

from typing import Literal, NamedTuple, TypeAlias

from pandas import DataFrame, Series

DfOrS: TypeAlias = DataFrame | Series  # pyright: ignore[reportMissingTypeArgument]

# * MARK: settings

BuildMode: TypeAlias = Literal["dev", "docs"]
NbExecutionMode: TypeAlias = Literal["off", "force", "auto", "cache", "inline"]

# * MARK: intersphinx


class IspxMappingValue(NamedTuple):
    """Intersphinx mapping value."""

    url: str
    path: str | None = None


# * MARK: docstrings
SeeAlsoReference: TypeAlias = tuple[str, None]
"""In all examples given, there is a "None" here, like (numpy.dot, None)."""
SeeAlsoRelationship: TypeAlias = list[str]
"""The (optional) relationship is empty if not provided, else one str per line."""
SingleSeeAlso: TypeAlias = tuple[list[SeeAlsoReference], SeeAlsoRelationship]
"""One "entry" in the See Also section."""
SeeAlsoSection: TypeAlias = list[SingleSeeAlso]
"""The full "See Also" section, as returned by `numpydoc.docscrape.NumpyDoc`."""
RegularSection: TypeAlias = list[str]
"""One list element per (unstripped) line of input."""
