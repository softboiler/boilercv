"""Model for `dvc.yaml`.

Adapted from [iterative/dvcyaml-schema](https://github.com/iterative/dvcyaml-schema).
See original license below.

Notes
-----
The original license is reproduced below.

Copyright 2020-2021 Iterative, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from types import NoneType
from typing import Annotated, Any, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

FilePath: TypeAlias = str
VarKey: TypeAlias = str
StageName: TypeAlias = str
PlotIdOrFilePath: TypeAlias = str
PlotColumn: TypeAlias = str
PlotColumns: TypeAlias = str
PlotTemplateName: TypeAlias = str


class OutFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cache: bool | None = Field(True, description="Cache output by DVC")
    persist: bool | None = Field(False, description="Persist output between runs")
    checkpoint: bool | None = Field(
        False,
        description="Indicate that the output is associated with "
        "in-code checkpoints",
    )
    desc: str | None = Field(
        None, description="User description for the output", title="Description"
    )
    type: str | None = Field(
        None, description="User assigned type of the output", title="Type"
    )
    labels: list[str] | None = Field(
        default_factory=set,
        description="User assigned labels of the output",
        title="Labels",
    )
    meta: dict[str, Any] | None = Field(
        None, description="Custom metadata of the output.", title="Meta"
    )
    remote: str | None = Field(
        None, description="Name of the remote to use for pushing/fetching"
    )
    push: bool | None = Field(
        True,
        description="Whether the output should be pushed to remote "
        "during `dvc push`",
    )


class PlotFlags(OutFlags):
    x: PlotColumn = Field(None, description="Default field name to use as x-axis data")
    y: PlotColumn = Field(None, description="Default field name to use as y-axis data")
    x_label: str = Field(None, description="Default label for the x-axis")
    y_label: str = Field(None, description="Default label for the y-axis")
    title: str = Field(None, description="Default plot title")
    header: bool = Field(
        False, description="Whether the target CSV or TSV has a header or not"
    )
    template: FilePath = Field(None, description="Default plot template")


X = Annotated[dict[FilePath, PlotColumn], Field(default_factory=dict)]


Y = Annotated[dict[FilePath, PlotColumns], Field(default_factory=dict)]


class TopLevelPlotFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: PlotColumn | X = Field(
        None,
        description=(
            "A single column name, or a dictionary of data-source and column pair"
        ),
    )
    y: PlotColumns | Y = Field(
        default_factory=dict,
        description=(
            "A single column name, list of columns,"
            " or a dictionary of data-source and column pair"
        ),
    )
    x_label: str = Field(None, description="Default label for the x-axis")
    y_label: str = Field(None, description="Default label for the y-axis")
    title: str = Field(None, description="Default plot title")
    template: str = Field(default="linear", description="Default plot template")


EmptyTopLevelPlotFlags = Annotated[NoneType, Field(default=None)]


class TopLevelArtifactFlags(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = Field(description="Path to the artifact")
    type: str = Field(None, description="Type of the artifact")
    desc: str = Field(None, description="Description for the artifact")
    meta: dict[str, Any] = Field(None, description="Custom metadata for the artifact")
    labels: list[str] = Field(
        default_factory=set, description="Labels for the artifact"
    )


DEP_DESC = "Path to a dependency (input) file or directory for the stage."


DepModel = Annotated[FilePath, Field(..., description=DEP_DESC)]


Dependencies: TypeAlias = list[DepModel]


ParamKey = Annotated[str, Field(..., description="Parameter name (dot-separated).")]


CustomParamFileKeys = Annotated[
    dict[FilePath, list[ParamKey]],
    Field(..., description="Path to YAML/JSON/TOML/Python params file."),
]


EmptyParamFileKeys = Annotated[
    dict[FilePath, None],
    Field(..., description="Path to YAML/JSON/TOML/Python params file."),
]


Param = ParamKey | CustomParamFileKeys | EmptyParamFileKeys


Params = list[Param]


Out = Annotated[
    FilePath | dict[FilePath, OutFlags],
    Field(..., description="Path to an output file or dir of the stage."),
]


Outs = list[Out]


Metric = Annotated[
    FilePath | dict[FilePath, OutFlags],
    Field(..., description="Path to a JSON/TOML/YAML metrics output of the stage."),
]


PLOT_DESC = """\
Path to plots file or dir of the stage.

Data files may be JSON/YAML/CSV/TSV.

Image files may be JPEG/GIF/PNG."""


Plot = Annotated[
    FilePath | dict[FilePath, PlotFlags], Field(..., description=PLOT_DESC)
]

Plots = list[Plot]


VarPath = Annotated[
    str, Field(..., description="Path to params file with values for substitution.")
]


VarDecl = Annotated[
    dict[VarKey, Any], Field(..., description="Dict of values for substitution.")
]


Vars = list[VarPath | VarDecl]


STAGE_VARS_DESC = """\
List of stage-specific values for substitution.

May include any dict or a path to a params file.

Use in the stage with the `${}` substitution expression."""

CMD_DESC = """\
(Required) Command to run (anything your system terminal can run).

Can be a string or a list of commands."""

PARAMS_DESC = """\
List of dot-separated parameter dependency keys to track from `params.yaml`.

May contain other YAML/JSON/TOML/Python parameter file names, with a \
sub-list of the param names to track in them (leave empty to include all).\
"""

METRICS_DESC = "List of metrics of the stage written to JSON/TOML/YAML."

PLOTS_DESC = """\
List of plots of the stage for visualization.

Plots may be written to JSON/YAML/CSV/TSV for data or JPEG/GIF/PNG for images.\
"""


class Stage(BaseModel):
    """A named stage of a pipeline."""

    model_config = ConfigDict(extra="forbid")
    cmd: str | list[str] = Field(..., description=CMD_DESC)
    wdir: str | None = Field(
        None, description="Working directory for the cmd, relative to `dvc.yaml`"
    )
    deps: Dependencies | None = Field(
        None, description="List of the dependencies for the stage."
    )
    params: Params | None = Field(None, description=PARAMS_DESC)
    outs: Outs | None = Field(None, description="List of the outputs of the stage.")
    metrics: Outs | None = Field(None, description=METRICS_DESC)
    plots: Plots | None = Field(None, description=PLOTS_DESC)
    frozen: bool | None = Field(False, description="Assume stage as unchanged")
    always_changed: bool | None = Field(
        False, description="Assume stage as always changed"
    )
    vars: Vars | None = Field(None, description=STAGE_VARS_DESC)
    desc: str | None = Field(None, description="Description of the stage")
    meta: Any = Field(None, description="Additional information/metadata")


FOREACH_DESC = """\
Iterable to loop through in foreach. Can be a parametrized string, list or \
a dict.

The stages will be generated by iterating through this data, by substituting \
data in the `do` block."""

DO_DESC = """\
Parametrized stage definition that'll be substituted over for each of the \
value from the foreach data."""


ParametrizedString = Annotated[str, Field(pattern=r"^\$\{.*?\}$")]


class ForeachDo(BaseModel):
    model_config = ConfigDict(frozen=False, extra="forbid")
    foreach: (
        Annotated[str, Field(pattern=r"^\$\{.*?\}$")] | list[Any] | dict[str, Any]
    ) = Field(..., description=FOREACH_DESC)
    do: Stage = Field(..., description=DO_DESC)


MATRIX_DESC = """\
Generate stages based on combination of variables.

The variable can be a list of values, or a parametrized string referencing a \
list."""


class Matrix(Stage):
    model_config = ConfigDict(frozen=False, extra="forbid")
    matrix: dict[str, list[Any] | ParametrizedString] = Field(
        ..., description=MATRIX_DESC
    )


Definition = ForeachDo | Matrix | Stage


VARS_DESC = """\
List of values for substitution.

May include any dict or a path to a params file which may be a string or a \
dict to params in the file).

Use elsewhere in `dvc.yaml` with the `${}` substitution expression."""


TopLevelPlots = Annotated[
    dict[PlotIdOrFilePath, TopLevelPlotFlags | EmptyTopLevelPlotFlags],
    Field(default_factory=dict),
]


TopLevelPlotsList = Annotated[
    list[PlotIdOrFilePath | TopLevelPlots], Field(default_factory=list)
]


ArtifactIdOrFilePath = Annotated[
    str, Field(pattern=r"^[a-z0-9]([a-z0-9-/]*[a-z0-9])?$")
]


TopLevelArtifacts = Annotated[
    dict[ArtifactIdOrFilePath, TopLevelArtifactFlags], Field(default_factory=dict)
]


class DvcYamlModel(BaseModel):
    model_config = ConfigDict(title="dvc.yaml", extra="forbid")

    vars: Vars = Field(default_factory=list, description=VARS_DESC, title="Variables")
    stages: dict[StageName, Definition] = Field(
        default_factory=dict, description="List of stages that form a pipeline."
    )
    plots: TopLevelPlots | TopLevelPlotsList = Field(
        default_factory=dict, description="Top level plots definition."
    )
    params: list[FilePath] = Field(
        default_factory=set, description="List of parameter files"
    )
    metrics: list[FilePath] = Field(
        default_factory=set, description="List of metric files"
    )
    artifacts: TopLevelArtifacts = Field(
        default_factory=dict, description="Top level artifacts definition."
    )
