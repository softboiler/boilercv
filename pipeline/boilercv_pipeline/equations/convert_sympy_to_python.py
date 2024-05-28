"""Convert SymPy equations to Python functions."""

from loguru import logger
from sympy import parse_expr, symbols
from tqdm import tqdm

from boilercv_pipeline.correlations.dimensionless_bubble_diameter import EQUATIONS
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.equations import (
    SYMPY_SUBS,
)

syms = tuple(SYMPY_SUBS.values())
local_dict = dict(zip(syms, symbols(syms), strict=True))


def main():  # noqa: D103
    for expression in tqdm(EQUATIONS.values()):  # pyright: ignore[reportArgumentType, reportCallIssue]  1.1.356, tomlkit 0.12.4
        eq = expression["sympy"]
        if not eq:
            continue
        eq = eq.strip().replace("\n", "").replace("    ", "")
        if expression["python"]:
            continue
        for symbol, sub in SYMPY_SUBS.items():
            eq = eq.replace(symbol, sub)
        eq = parse_expr(eq, local_dict=local_dict, evaluate=False)
    #     toml[EQS][i][PYTHON] = (  # pyright: ignore[reportArgumentType, reportIndexIssue]  1.1.356, tomlkit 0.12.4
    #         lambdastr(
    #             expr=eq.rhs,
    #             args=[s for s in eq.rhs.free_symbols if s.name in ARGS.values()],
    #         )
    #         .split(":")[-1]
    #         .strip()
    #         .removeprefix("(")
    #         .removesuffix(")")
    #     )
    # data = dumps(toml)
    # for old, new in TOML_REPL.items():
    #     data = data.replace(old, new)
    # TOML.write_text(encoding="utf-8", data=data)


if __name__ == "__main__":
    logger.info("Start converting SymPy expressions to Python functions")
    main()
    logger.info("Finish converting SymPy expressions to Python functions")
