"""Synchronize DVC config and parameters with the pipeline."""

import dataclasses
from collections.abc import Sized
from dataclasses import dataclass
from pathlib import Path
from types import NoneType
from typing import Any, ClassVar, get_args

from cappa.base import command
from more_itertools import one
from pydantic import BaseModel, Field, create_model
from yaml import safe_dump

from boilercv.contexts import CONTEXT
from boilercv_pipeline.cli.types import Model_T, RelativePath, Stages
from boilercv_pipeline.models import dvc as _dvc
from boilercv_pipeline.models.contexts import BOILERCV_PIPELINE, DVC, PARAMS, ROOTED
from boilercv_pipeline.models.path import (
    BoilercvPipelineContextModel,
    get_boilercv_pipeline_config,
)


@dataclass
class SyncedDvcModel:
    """Synced DVC model."""

    model: _dvc.DvcYamlModel = dataclasses.field(default_factory=_dvc.DvcYamlModel)
    """DVC model."""
    params: dict[str, Any] = dataclasses.field(default_factory=dict)
    """Parameters."""


@command(name="sync-dvc")
class SyncDVC(BaseModel):
    """Generate `dvc.yaml`."""

    root: ClassVar[Path] = Path.cwd()
    """Root directory for synced DVC configurations.

    Currently, must be the current working directory as it is tied to the module
    constant {obj}`boilercv_pipeline.models.contexts.ROOTED`.
    """
    yaml: RelativePath = Path("dvc.yaml")
    """DVC's primary config YAML file."""
    params: RelativePath = Path("dvc.yaml")
    """DVC's primary parameters YAML file."""

    def __call__(self):
        """Sync `dvc.yaml`."""
        synced = self.get_dvc_model()
        (self.root / self.yaml).write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False,
                indent=2,
                data=synced.model.model_dump(exclude_none=True),
            ),
        )
        (self.root / self.params).write_text(
            encoding="utf-8",
            data=safe_dump(sort_keys=True, indent=2, data=synced.params),
        )

    @classmethod
    def get_dvc_model(cls) -> SyncedDvcModel:
        """Get DVC model."""
        Model = BoilercvPipelineContextModel  # noqa: N806
        config = Model.model_config
        try:
            Model.model_config = get_boilercv_pipeline_config(ROOTED, dvc=True)
            dvc = create_model(  # pyright: ignore[reportCallIssue]
                "_Stages",
                __base__=Model,
                **{  # pyright: ignore[reportArgumentType]
                    s.__module__.split(".")[-1]: (s, Field(default_factory=s))
                    for s in get_args(Stages)
                },
            )().model_dump()[CONTEXT][BOILERCV_PIPELINE][DVC]
            (Path.cwd() / "params.yaml").write_text(
                encoding="utf-8",
                data=safe_dump(sort_keys=True, indent=2, data=dvc[PARAMS]),
            )
        finally:
            Model.model_config = config
        return SyncedDvcModel(
            model=cls.clear_defaults(_dvc.DvcYamlModel.model_validate(dvc[DVC])),
            params=dvc["params"],
        )

    @classmethod
    def clear_dvc_defaults(cls, model: _dvc.DvcYamlModel):
        """Clear defaults in DVC model and its nested stages."""
        model = cls.clear_defaults(_dvc.DvcYamlModel.model_validate(model))
        for name, stage in model.stages.items():
            if isinstance(stage, _dvc.Stage):
                stage = cls.clear_defaults(stage)
                for i, out in enumerate(stage.outs):
                    if isinstance(out, dict):
                        stage.outs[i] = {
                            one(out.keys()): cls.clear_defaults(one(out.values()))
                        }
                model.stages[name] = stage

    @classmethod
    def clear_defaults(cls, model: Model_T) -> Model_T:
        """Clear default fields of a model."""
        model = model.model_copy(deep=True)
        for (field, value), info in zip(
            dict(model).items(), model.model_fields.values(), strict=True
        ):
            if (
                value is not None  # noqa: PLR0916
                and (ann := info.annotation)
                and (
                    (isinstance(value, Sized) and not len(value))
                    or (value == info.default and NoneType in get_args(ann))
                )
            ):
                setattr(model, field, None)
        return model
