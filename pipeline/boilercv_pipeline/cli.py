"""Command-line interface."""

from dataclasses import dataclass
from json import loads
from typing import Any

from cappa.base import command
from cappa.command import Command
from cappa.output import Output
from cappa.parser import backend
from cappa.subcommand import Subcommands

from boilercv_pipeline.models.generated.stages.binarize import Binarize
from boilercv_pipeline.models.generated.stages.convert import Convert
from boilercv_pipeline.models.generated.stages.fill import Fill
from boilercv_pipeline.models.generated.stages.find_contours import FindContours
from boilercv_pipeline.models.generated.stages.flatten_data_dir import FlattenDataDir
from boilercv_pipeline.models.generated.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.models.generated.stages.preview_filled import PreviewFilled
from boilercv_pipeline.models.generated.stages.preview_gray import PreviewGray


@command(invoke="boilercv_pipeline.models.Params")
class SyncParams:
    """Synchronize parameters."""


@command(invoke="boilercv_pipeline.models.types.generated.sync_stages")
class SyncStagesLiterals:
    """Sync stages literals."""


@dataclass
class Stages:
    """Stages."""

    commands: Subcommands[
        Binarize
        | Convert
        | Fill
        | FindContours
        | FlattenDataDir
        | PreviewBinarized
        | PreviewFilled
        | PreviewGray,
    ]


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncParams | SyncStagesLiterals | Stages]


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
