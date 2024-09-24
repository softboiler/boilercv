"""Synchronize DVC config and parameters with the pipeline."""

from collections.abc import Sized
from pathlib import Path
from types import NoneType
from typing import ClassVar, get_args

from cappa.base import command
from more_itertools import one
from pydantic import BaseModel, Field, create_model
from yaml import safe_dump

from boilercv_pipeline.cli.types import Model_T, RelativePath, Stages
from boilercv_pipeline.models import dvc as _dvc
from boilercv_pipeline.models.contexts import DVC, ROOTED, DvcContext
from boilercv_pipeline.models.path import (
    BoilercvPipelineContextStore,
    get_boilercv_pipeline_config,
)


@command(name="sync-dvc")
class SyncDVC(BaseModel):
    """Generate `dvc.yaml`."""

    root: ClassVar[Path] = Path.cwd()
    """Root directory for synced DVC configurations.

    Currently, must be the current working directory as it is tied to the module
    constant {obj}`boilercv_pipeline.models.contexts.ROOTED`.
    """
    pipeline: RelativePath = Path("dvc.yaml")
    """Primary config file describing the DVC pipeline."""
    params: RelativePath = Path("params.yaml")
    """DVC's primary parameters YAML file."""

    def __call__(self):
        """Sync `dvc.yaml`."""
        synced = self.get_dvc_model()
        (self.root / self.pipeline).write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False,
                indent=2,
                data=self.clear_dvc_defaults(synced.model).model_dump(
                    exclude_none=True
                ),
                width=float("inf"),
            ),
        )
        (self.root / self.params).write_text(
            encoding="utf-8",
            data=safe_dump(
                sort_keys=False, indent=2, data=synced.params, width=float("inf")
            ),
        )

    @classmethod
    def get_dvc_model(cls) -> DvcContext:
        """Get DVC model."""
        Model = BoilercvPipelineContextStore  # noqa: N806
        config = Model.model_config
        stages = get_args(Stages)
        try:
            Model.model_config = get_boilercv_pipeline_config(ROOTED, dvc=True)
            model = create_model(  # pyright: ignore[reportCallIssue]
                "_Stages",
                __base__=Model,
                **{  # pyright: ignore[reportArgumentType]
                    s.__module__.split(".")[-1]: (s, Field(default_factory=s))
                    for s in stages
                },
            )
        finally:
            Model.model_config = config
        return model().context[DVC]

    @classmethod
    def clear_dvc_defaults(cls, model: _dvc.DvcYamlModel) -> _dvc.DvcYamlModel:
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
        return model

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
