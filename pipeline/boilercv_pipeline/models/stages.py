"""Stages."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from re import match
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field
from yaml import safe_load

from boilercv.mappings import apply
from boilercv.morphs.morphs import Morph
from boilercv_pipeline.models.types.generated.stages import ManualStageName, StageName


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


class DvcStages(Morph[StageName | ManualStageName, DvcStage]):
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
                safe_load(dvc.read_text(encoding="utf-8")) or {}
                if dvc.exists()
                else {},
                leaf_fun=apply_inner,
            )["stages"]
        )
