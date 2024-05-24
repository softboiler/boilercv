"""Equations."""

from boilercv_pipeline.correlations.types import Forms, FormsRepl
from boilercv_pipeline.morphs import replace


def set_param_forms(i: Forms, name: str = "") -> Forms:
    """Set forms for parameters."""
    if i["sympy"] and not i["latex"]:
        i["latex"] = i["sympy"]
    if not i["latex"]:
        i["latex"] = rf"\{name}"
    return i


LATEX_PARAMS = {
    name: (
        param.pipe(set_param_forms, name=name).pipe(
            replace,
            repls=[
                FormsRepl(src="latex", dst="sympy", find=k, repl=v)
                for k, v in {r"_\b0": "_bo", r"_\o": "_0", "\\": ""}.items()
            ],
        )
    )
    for name, param in {
        "bubble_fourier": Forms({"latex": r"\Fo_\o"}),
        "bubble_jakob": Forms({"latex": r"\Ja"}),
        "bubble_initial_reynolds": Forms({"latex": r"\Re_\bo"}),
        **{n: Forms({"latex": f"\\{n}"}) for n in ["beta", "pi"]},
    }.items()
}
"""Parameters for function calls."""
SYMPY_SUBS = {arg["sympy"]: name for name, arg in LATEX_PARAMS.items()}
"""Substitutions from SymPy symbolic variables to descriptive names."""
