"""Command-line interface."""

from collections.abc import Sized
from dataclasses import dataclass
from pathlib import Path
from types import NoneType
from typing import Self, get_args

from cappa.base import command
from cappa.subcommand import Subcommands
from pydantic import (
    BaseModel,
    Field,
    SerializerFunctionWrapHandler,
    model_serializer,
    model_validator,
)
from yaml import safe_dump

from boilercv.contexts import CONTEXT
from boilercv_pipeline.models import dvc
from boilercv_pipeline.models.contexts import BOILERCV_PIPELINE, ROOTED
from boilercv_pipeline.models.contexts.types import BoilercvPipelineSerializationInfo
from boilercv_pipeline.models.dvc import OutFlags
from boilercv_pipeline.models.path import (
    BoilercvPipelineCtxModel,
    get_boilercv_pipeline_config,
)
from boilercv_pipeline.stages.binarize import Binarize
from boilercv_pipeline.stages.convert import Convert
from boilercv_pipeline.stages.fill import Fill
from boilercv_pipeline.stages.find_contours import FindContours
from boilercv_pipeline.stages.find_objects import FindObjects
from boilercv_pipeline.stages.find_tracks import FindTracks
from boilercv_pipeline.stages.get_mae import GetMae
from boilercv_pipeline.stages.get_thermal_data import GetThermalData
from boilercv_pipeline.stages.preview_binarized import PreviewBinarized
from boilercv_pipeline.stages.preview_filled import PreviewFilled
from boilercv_pipeline.stages.preview_gray import PreviewGray
from boilercv_pipeline.stages.skip_cloud import SkipCloud


class Constants(BaseModel):
    """Constants."""

    dvc_out_config: OutFlags = OutFlags(persist=True)
    """Default `dvc.yaml` configuration for `outs`."""
    skip_cloud: list[str] = ["data/cines", "data/large_sources"]
    """These paths are too large and unwieldy to cache or push to cloud storage."""
    dvc_out_skip_cloud_config: OutFlags = OutFlags(
        cache=False, persist=True, push=False
    )
    """Default `dvc.yaml` configuration for `outs` that skip the cloud."""


const = Constants()


@dataclass
class Stage:
    """Stage."""

    commands: Subcommands[
        SkipCloud
        | Convert
        | Binarize
        | PreviewGray
        | PreviewBinarized
        | FindContours
        | Fill
        | PreviewFilled
        | GetThermalData
        | FindObjects
        | FindTracks
        | GetMae
    ]


def clear_default_fields(model: BaseModel):
    """Clear default fields of a model."""
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


@command(name="sync-dvc")
class SyncDVC:
    """Generate `dvc.yaml`."""

    def __call__(self):
        """Sync `dvc.yaml`."""

        class Stages(BoilercvPipelineCtxModel):
            """Stages."""

            model_config = get_boilercv_pipeline_config(
                ROOTED, resolve_rooted=True, sync_dvc=True
            )

            skip_cloud: SkipCloud = Field(default_factory=SkipCloud)
            convert: Convert = Field(default_factory=Convert)
            binarize: Binarize = Field(default_factory=Binarize)
            preview_gray: PreviewGray = Field(default_factory=PreviewGray)
            preview_binarized: PreviewBinarized = Field(
                default_factory=PreviewBinarized
            )
            find_contours: FindContours = Field(default_factory=FindContours)
            fill: Fill = Field(default_factory=Fill)
            preview_filled: PreviewFilled = Field(default_factory=PreviewFilled)
            get_thermal_data: GetThermalData = Field(default_factory=GetThermalData)
            find_objects: FindObjects = Field(default_factory=FindObjects)
            find_tracks: FindTracks = Field(default_factory=FindTracks)
            get_mae: GetMae = Field(default_factory=GetMae)

            @model_validator(mode="after")
            def dvc_validate_stages(self) -> Self:
                """Validate stages for `dvc.yaml`."""
                if (ctx := self.context[BOILERCV_PIPELINE]).sync_dvc:
                    ctx.dvc.stages = {
                        name: dvc.Stage(
                            cmd=f"boilercv-pipeline stage {name.replace('_', '-')}"
                        )
                        for name in [f for f in self.model_fields if f != CONTEXT]
                    }
                return self

            @model_serializer(mode="wrap")
            def dvc_serialize_stages(
                self,
                nxt: SerializerFunctionWrapHandler,
                ser_info: BoilercvPipelineSerializationInfo,
            ) -> str:
                """Serialize stages for `dvc.yaml`."""
                ser = nxt(self)
                dvc_model = ser_info.context[BOILERCV_PIPELINE].dvc
                clear_default_fields(dvc_model)
                for stage in dvc_model.stages.values():
                    if isinstance(stage, dvc.Stage):
                        clear_default_fields(stage)
                (Path.cwd() / "dvc.yaml").write_text(
                    encoding="utf-8",
                    data=safe_dump(
                        sort_keys=False,
                        indent=2,
                        data=dvc_model.model_dump(exclude_none=True),
                    ),
                )
                return ser

        Stages().model_dump()
        # def process_path(path: Path | str) -> str:
        #     path = Path(path)
        #     return (
        #         path.relative_to(self.root) if path.is_absolute() else path
        #     ).as_posix()
        # stages: dict[str, dvc.Stage] = {}
        # all_params: dict[str, AnyParams] = dict(Stages())
        # del all_params["context"]
        # for name, params in all_params.items():
        #     outs: dict[str, str | dict[str, Any]] = params.outs.model_dump()
        #     plots: str | None = outs.pop("plots", None)  # pyright: ignore[reportAssignmentType]
        #     stages[name] = dvc.Stage(
        #         cmd=f"boilercv-pipeline stage {name.replace('_', '-')}",
        #         deps=([
        #             process_path(d)
        #             for k, d in params.deps.model_dump().items()
        #             if k != "context"
        #         ]),
        #         outs=([
        #             (
        #                 {out: const.dvc_out_skip_cloud_config}
        #                 if out in const.skip_cloud
        #                 else {out: const.dvc_out_config}
        #             )
        #             for out in outs.values()
        #             if isinstance(out, str | Path)
        #         ]),
        #         plots=[p.as_posix() for p in Path(plots).iterdir()] if plots else [],
        #     )


@dataclass
class BoilercvPipeline:
    """Pipeline."""

    commands: Subcommands[SyncDVC | Stage]
