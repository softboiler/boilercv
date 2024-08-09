"""Data pipeline."""

from collections.abc import Callable
from json import loads
from os import environ
from pathlib import Path
from typing import Any

from cappa.command import Command
from cappa.output import Output
from cappa.parser import backend
from loguru import logger
from pandas import set_option

PROJECT_PATH = Path.cwd()
"""Path to the project root, where `params.yaml` will go."""

_debug = environ.get("BOILERCV_DEBUG")
_preview = environ.get("BOILERCV_PREVIEW")
_write = environ.get("BOILERCV_WRITE")
_build_docs = environ.get("BOILERCV_BUILD_DOCS")
DEBUG = str(_debug).casefold() == "true" if _debug else False
"""Whether to run in debug mode. Log to `boilercv.log`."""
PREVIEW = str(_preview).casefold() == "true" if _preview else False
"""Whether to run interactive previews."""
WRITE = str(_write).casefold() == "true" if _write else False
"""Whether to write to the local media folder."""
BUILD_DOCS = str(_build_docs).casefold() == "true" if _build_docs else False


def init():
    """Initialize `boilercv`."""
    if DEBUG:
        logger.add(sink="boilercv.log")
    set_option("mode.copy_on_write", True)
    set_option("mode.chained_assignment", "raise")
    set_option("mode.string_storage", "pyarrow")


init()


def run_example(func: Callable[..., Any], preview: bool = False) -> tuple[str, Any]:
    """Run an example file, logging the module name containing the function.

    Args:
        func: The example function to run.
        preview: Preview results from the function. Default: False.
    """
    module_name = func.__module__
    logger.info(f'Running example "{module_name}"')
    result = func(preview=preview)
    return module_name, result


def defaults_backend(
    command: Command[Any],
    argv: list[str],
    output: Output,
    prog: str,
    provide_completions: bool = False,
) -> tuple[Any, Command[Any], dict[str, Any]]:
    """Backend that injects defaults and makes `model_validate` the parse callable."""
    parser, parsed_command, parsed_args = backend(
        command=command,
        argv=argv,
        output=output,
        prog=prog,
        provide_completions=provide_completions,
    )
    if (cmds := parsed_args.get("commands")) and cmds["__name__"] != "stages":
        return parser, parsed_command, parsed_args
    extra_args = ["help", "completion"]
    defaults: dict[str, dict[str, Any]] = {}
    for arg in parsed_command.arguments:
        if arg.value_name in extra_args:  # pyright: ignore[reportAttributeAccessIssue]
            continue
        arg.parse = arg.parse.model_validate  # pyright: ignore[reportAttributeAccessIssue, reportFunctionMemberAccess, reportOptionalMemberAccess]
        defaults[arg.value_name] = arg.default.model_dump_json()  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    return (
        parser,
        parsed_command,
        {
            k: loads(v) if isinstance(v, str) else v
            for k, v in {**defaults, **parsed_args}.items()
        },
    )
