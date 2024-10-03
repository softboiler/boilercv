"""Sync `dvc.yaml` and `params.yaml` with pipeline specification."""

from collections.abc import Sized
from importlib import import_module
from inspect import getmembers, ismodule
from pathlib import Path
from types import NoneType
from typing import get_args

from context_models import CONTEXT, ContextStore
from context_models.types import Context
from dev.tools.environment import run
from more_itertools import one
from pydantic import BaseModel, create_model
from pydantic.alias_generators import to_pascal
from yaml import safe_dump, safe_load

from boilercv_pipeline.models.contexts import ROOTED
from boilercv_pipeline.models.path import (
    BoilercvPipelineContextStore,
    get_boilercv_pipeline_context,
)
from boilercv_pipeline.parser import invoke
from boilercv_pipeline.sync_dvc import SyncDvc
from boilercv_pipeline.sync_dvc.contexts import DVC, DvcContext, DvcContexts
from boilercv_pipeline.sync_dvc.dvc import DvcYamlModel, Stage
from boilercv_pipeline.sync_dvc.types import Model


class Constants(BaseModel):
    """Constants."""

    root: Path = Path.cwd()
    """Root directory for synced DVC configurations.

    Currently, must be the current working directory as it is tied to the module
    constant {obj}`boilercv_pipeline.models.contexts.ROOTED`.
    """
    stages: str = "boilercv_pipeline.stages"
    model: type[ContextStore] = BoilercvPipelineContextStore
    context: Context = get_boilercv_pipeline_context(ROOTED)


const = Constants()


def main(params: SyncDvc):
    """Sync `dvc.yaml` and `params.yaml` with pipeline specification."""
    dvc = get_dvc_context(
        params=(
            safe_load(params.params.read_text(encoding="utf-8"))
            if params.params.exists()
            else {}
        ),
        model=const.model,
        context=const.context,
        stages=const.stages,
    )
    (const.root / params.pipeline).write_text(
        encoding="utf-8",
        data=safe_dump(
            indent=2,
            width=float("inf"),
            data=dvc_clear_defaults(dvc.model).model_dump(exclude_none=True),
        ),
    )
    (const.root / params.params).write_text(
        encoding="utf-8",
        data=safe_dump(
            indent=2,
            width=float("inf"),
            data={
                **dvc.params,
                **(
                    {}
                    if params.update_param_values or not params.params.exists()
                    else {
                        k: v
                        for k, v in safe_load(
                            params.params.read_text(encoding="utf-8")
                        ).items()
                        if k in dvc.params
                    }
                ),
            },
        ),
    )
    run("pre-commit run --all-files prettier", check=False, capture_output=True)


def get_dvc_context(
    params, model: type[ContextStore], context: Context, stages: str
) -> DvcContext:
    """Get DVC context for pipeline model and stages."""

    class CombinedContext(model.model_fields["context"].annotation, DvcContexts): ...  # pyright: ignore[reportGeneralTypeIssues]

    stage_models = {
        k: dict(getmembers(v))[to_pascal(k)]
        for k, v in getmembers(import_module(stages))
        if ismodule(v)
    }
    return create_model(  # pyright: ignore[reportCallIssue]
        "_Stages",
        __base__=model,
        **{k: (v, ...) for k, v in {CONTEXT: CombinedContext, **stage_models}.items()},  # pyright: ignore[reportArgumentType]
    )(**{
        CONTEXT: {**context, **DvcContexts(dvc=DvcContext())},
        **{
            field: {
                k: (("--no" not in v) if isinstance(v, str) and "--" in v else v)
                for k, v in params.items()
                if k in stage.model_fields
            }
            for field, stage in stage_models.items()
            if field != CONTEXT
        },
    }).context[DVC]


def dvc_clear_defaults(model: DvcYamlModel) -> DvcYamlModel:
    """Clear defaults in DVC model and its nested stages."""
    model = clear_defaults(DvcYamlModel.model_validate(model))
    for name, stage in model.stages.items():
        if isinstance(stage, Stage):
            stage = clear_defaults(stage)
            for i, out in enumerate(stage.outs):
                if isinstance(out, dict):
                    stage.outs[i] = {one(out.keys()): clear_defaults(one(out.values()))}
            model.stages[name] = stage
    return model


def clear_defaults(model: Model) -> Model:
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


if __name__ == "__main__":
    invoke(SyncDvc)
