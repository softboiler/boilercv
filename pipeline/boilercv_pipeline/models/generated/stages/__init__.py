"""Stages."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from re import match
from shlex import quote
from subprocess import run
from textwrap import dedent
from typing import Any, Self

from copier import get_args
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal
from yaml import safe_load

from boilercv.mappings import apply
from boilercv.morphs.morphs import Morph
from boilercv_pipeline.config import const
from boilercv_pipeline.models.generated.types.stages import StageName


class OutsConfig(BaseModel):
    """Config for outputs."""

    model_config = ConfigDict(use_attribute_docstrings=True)
    persist: bool = True


class DvcStage(BaseModel):
    """Stage from DVC."""

    model_config = ConfigDict(use_attribute_docstrings=True)
    cmd: str = ""
    """Command to run."""
    deps: list[Path] = Field(default_factory=list)
    """Stage dependencies."""
    outs: list[Path | dict[Path, OutsConfig]] = Field(default_factory=list)
    """Stage outputs."""


class DvcStages(Morph[StageName, DvcStage]):
    """Stages from DVC."""

    @classmethod
    def from_defaults(cls) -> Self:
        """Generate stages from default values."""
        dvc = Path.cwd() / "dvc.yaml"
        dvc_params = Path.cwd() / "params.yaml"
        params = (
            safe_load(dvc_params.read_text(encoding="utf-8")) or {}
            if dvc_params.exists()
            else {}
        )

        def replace_template(v: str) -> str:
            """Replace templated string."""
            repl = ""
            while match_ := match(r"^(?P<bef>.*)\${(?P<template>.+)}(?P<aft>.*)$", v):
                repl = params
                for key in match_["template"].split("."):
                    repl = repl[key]
                v = match_.expand(rf"\g<bef>{repl}\g<aft>")
            return v

        def apply_inner(v: Any) -> Any:
            """Apply a function to a path, sequence of paths, or mapping of names to paths."""
            match v:
                case bool():
                    return v
                case str():
                    return replace_template(v)
                case Sequence():
                    return [apply_inner(v) for v in v]
                case Mapping():
                    return {apply_inner(k): apply_inner(v) for k, v in v.items()}
                case _:
                    return replace_template(v)

        return cls(
            apply(
                safe_load(dvc.read_text(encoding="utf-8").replace("# ", "")) or {}
                if dvc.exists()
                else {},
                leaf_fun=apply_inner,
            )["stages"]
        )


def data(path: Path) -> bool:
    """Path is data."""
    return path.as_posix().startswith("data")


def sync_stages():
    """Sync generated stages."""
    stages = DvcStages.from_defaults()
    updated_stages: list[Path] = []
    src_sep = "\n                "
    cmd_sep = " "
    for name, stage in [
        (name, const.package_dir / "models" / "generated" / "stages" / f"{name}.py")
        for name in get_args(StageName)
    ]:
        if stage.exists():
            continue
        updated_stages.append(stage)
        deps = src_sep.join([
            f"{path.stem}: Path = default.paths.{path.stem}"
            for path in stages[name].deps
            if data(path)
        ])
        outs = src_sep.join([
            f"{path.stem}: Path = default.paths.{path.stem}"
            for path in [
                (next(iter(out.keys())) if isinstance(out, dict) else out)
                for out in stages[name].outs
            ]
        ])
        src = dedent(f'''
            from pathlib import Path
            from typing import Annotated

            from boilercore.models import DefaultPathsModel
            from cappa.arg import Arg
            from cappa.base import command
            from pydantic import BaseModel, Field

            from boilercv_pipeline.models.config import default

            class Params(BaseModel):
                """Stage parameters."""

            class Deps(DefaultPathsModel):
                """Stage dependencies."""
                root: Path = Field(default=default.paths.root, exclude=True)
                {deps}

            class Outs(DefaultPathsModel):
                """Stage outputs."""
                root: Path = Field(default=default.paths.root, exclude=True)
                {outs}

            @command(invoke="boilercv_pipeline.stages.{name}.main")
            class {to_pascal(stage.stem)}(BaseModel):
                params: Annotated[Params, Arg(long=True)] = Params()
                deps: Annotated[Deps, Arg(long=True)] = Deps()
                outs: Annotated[Outs, Arg(long=True)] = Outs()
        ''')
        stage.write_text(encoding="utf-8", data=src)
    if not updated_stages:
        return
    paths = [f"{quote(stage.as_posix())}" for stage in updated_stages]
    run(
        check=True,
        args=[
            "pwsh",
            "-Command",
            cmd_sep.join([
                "scripts/Initialize-Shell.ps1;",
                "ruff check",
                *paths,
                ";",
                "ruff format",
                *paths,
            ]),
        ],
    )


sync_stages()
