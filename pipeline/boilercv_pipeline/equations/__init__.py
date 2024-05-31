"""Equation processing."""

from re import compile

from boilercv_pipeline.correlations.types.runtime import KeysPattern

equation_name_pattern = compile(
    r"""(?xm)^  # x: verbose, m: multiline, ^: begin, always use multiline https://web.archive.org/web/20240429145610/https://sethmlarson.dev/regex-$-matches-end-of-string-or-newline
    (?P<author>[\w_]+?)  # lazy so year is leftmost match
    _(?P<sort>  # sort on year and optional equation number
        (?P<year>\d{4})  # year must be four digits
        (?:_(?P<num>[\d_]+))?  # optionally, multiple equations from one paper
    )
    $"""  # end), group="", message=""),
)
keys_pattern = KeysPattern(
    pattern=equation_name_pattern,
    group="sort",
    apply_to_match=lambda i: [int(n) for n in i.split("_")],
    message="Couldn't find year in equation identifier '{key}' when sorting.",
)
