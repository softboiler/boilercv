"""Model for `dvc.yaml`.

Adapted from [iterative/dvcyaml-schema](https://github.com/iterative/dvcyaml-schema).

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

from collections.abc import Mapping, Sequence
from types import NoneType
from typing import Annotated, Any, TypeAlias

from pydantic import ConfigDict, Field

from boilercv.models import BaseModelDefaultAsNone

FilePath: TypeAlias = str
VarKey: TypeAlias = str
StageName: TypeAlias = str
PlotIdOrFilePath: TypeAlias = str
PlotColumn: TypeAlias = str
PlotColumns: TypeAlias = str
PlotTemplateName: TypeAlias = str


class DvcBaseModel(BaseModelDefaultAsNone, use_attribute_docstrings=True): ...


class OutFlags(DvcBaseModel):
    model_config = ConfigDict(extra="forbid")
    cache: bool | None = True
    """Cache output by DVC"""
    persist: bool | None = False
    """Persist output between runs"""
    checkpoint: bool | None = False
    """Indicate that the output is associated with in-code checkpoints"""
    desc: str | None = Field(default=None, title="Description")
    """User description for the output"""
    type: str | None = None
    """User assigned type of the output"""
    labels: Sequence[str] | None = None
    """User assigned labels of the output"""
    meta: Mapping[str, Any] | None = None
    """Custom metadata of the output."""
    remote: str | None = None
    """Name of the remote to use for pushing/fetching"""
    push: bool | None = True
    """Whether the output should be pushed to remote during `dvc push`"""


class PlotFlags(OutFlags):
    x: PlotColumn | None = None
    """Default field name to use as x-axis data"""
    y: PlotColumn | None = None
    """Default field name to use as y-axis data"""
    x_label: str | None = None
    """Default label for the x-axis"""
    y_label: str | None = None
    """Default label for the y-axis"""
    title: str | None = None
    """Default plot title"""
    header: bool = False
    """Whether the target CSV or TSV has a header or not"""
    template: FilePath | None = None
    """Default plot template"""


X: TypeAlias = Annotated[Mapping[FilePath, PlotColumn] | None, Field(default=None)]


Y: TypeAlias = Annotated[Mapping[FilePath, PlotColumns] | None, Field(default=None)]


class TopLevelPlotFlags(DvcBaseModel):
    model_config = ConfigDict(extra="forbid")
    x: PlotColumn | X = None
    """A single column name, or a dictionary of data-source and column pair"""
    y: PlotColumns | Y = None
    """A single column name, list of columns, or a dictionary of data-source and column pair"""
    x_label: str | None = None
    """Default label for the x-axis"""
    y_label: str | None = None
    """Default label for the y-axis"""
    title: str | None = None
    """Default plot title"""
    template: str = "linear"
    """Default plot template"""


EmptyTopLevelPlotFlags: TypeAlias = Annotated[NoneType, Field(default=None)]


class TopLevelArtifactFlags(DvcBaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    """Path to the artifact"""
    type: str | None = None
    """Type of the artifact"""
    desc: str | None = None
    """Description for the artifact"""
    meta: Mapping[str, Any] | None = None
    """Custom metadata for the artifact"""
    labels: Sequence[str] | None = None
    """Labels for the artifact"""


DepModel: TypeAlias = Annotated[
    FilePath,
    Field(description="Path to a dependency (input) file or directory for the stage."),
]


Dependencies: TypeAlias = Sequence[DepModel]


ParamKey: TypeAlias = Annotated[
    str, Field(description="Parameter name (dot-separated).")
]


CustomParamFileKeys: TypeAlias = Annotated[
    Mapping[FilePath, Sequence[ParamKey]],
    Field(description="Path to YAML/JSON/TOML/Python params file."),
]


EmptyParamFileKeys: TypeAlias = Annotated[
    Mapping[FilePath, None],
    Field(description="Path to YAML/JSON/TOML/Python params file."),
]


Param = ParamKey | CustomParamFileKeys | EmptyParamFileKeys


Params = Sequence[Param]


Out: TypeAlias = Annotated[
    FilePath | Mapping[FilePath, OutFlags],
    Field(description="Path to an output file or dir of the stage."),
]


Outs = Sequence[Out]


Metric: TypeAlias = Annotated[
    FilePath | Mapping[FilePath, OutFlags],
    Field(description="Path to a JSON/TOML/YAML metrics output of the stage."),
]


Plot: TypeAlias = Annotated[
    FilePath | Mapping[FilePath, PlotFlags],
    Field(
        description="""Path to plots file or dir of the stage.\n\nData files may be JSON/YAML/CSV/TSV.\n\nImage files may be JPEG/GIF/PNG."""
    ),
]
Plots = Sequence[Plot]
VarPath: TypeAlias = Annotated[
    str, Field(description="Path to params file with values for substitution.")
]
VarDecl: TypeAlias = Annotated[
    Mapping[VarKey, Any], Field(description="Dict of values for substitution.")
]
Vars = Sequence[VarPath | VarDecl]


class Stage(DvcBaseModel):
    """A named stage of a pipeline."""

    model_config = ConfigDict(extra="forbid")
    cmd: str | Sequence[str]
    """(Required) Command to run (anything your system terminal can run).\n\nCan be a string or a list of commands."""
    wdir: str | None = None
    """Working directory for the cmd, relative to `dvc.yaml`"""
    deps: Dependencies | None = None
    """List of the dependencies for the stage."""
    params: Params | None = None
    """List of dot-separated parameter dependency keys to track from `params.yaml`.\n\nMay contain other YAML/JSON/TOML/Python parameter file names, with a sub-list of the param names to track in them (leave empty to include all)."""
    outs: Outs | None = None
    """List of the outputs of the stage."""
    metrics: Outs | None = None
    """List of metrics of the stage written to JSON/TOML/YAML."""
    plots: Plots | None = None
    """List of plots of the stage for visualization.

    Plots may be written to JSON/YAML/CSV/TSV for data or JPEG/GIF/PNG for images."""
    frozen: bool | None = False
    """Assume stage as unchanged"""
    always_changed: bool | None = False
    """Assume stage as always changed"""
    vars: Vars | None = None
    """List of stage-specific values for substitution.

    May include any dict or a path to a params file.

    Use in the stage with the `${}` substitution expression.
    """
    desc: str | None = None
    """Description of the stage"""
    meta: Any = None
    """Additional information/metadata"""


ParametrizedString: TypeAlias = Annotated[str, Field(pattern=r"^\$\{.*?\}$")]


class ForeachDo(DvcBaseModel):
    model_config = ConfigDict(frozen=False, extra="forbid")
    foreach: ParametrizedString | Sequence[Any] | Mapping[str, Any]
    """Iterable to loop through in foreach. Can be a parametrized string, list or a dict.\n\nThe stages will be generated by iterating through this data, by substituting data in the `do` block."""
    do: Stage
    """Parametrized stage definition that'll be substituted over for each of the value from the foreach data."""


class Matrix(Stage):
    model_config = ConfigDict(frozen=False, extra="forbid")
    matrix: Mapping[str, Sequence[Any] | ParametrizedString] = Field(
        description="""Generate stages based on combination of variables.\n\nThe variable can be a list of values, or a parametrized string referencing a list."""
    )


Definition = ForeachDo | Matrix | Stage
TopLevelPlots: TypeAlias = Mapping[
    PlotIdOrFilePath, TopLevelPlotFlags | EmptyTopLevelPlotFlags
]
TopLevelPlotsList: TypeAlias = Sequence[PlotIdOrFilePath | TopLevelPlots]
ArtifactIdOrFilePath: TypeAlias = Annotated[
    str, Field(pattern=r"^[a-z0-9]([a-z0-9-/]*[a-z0-9])?$")
]
TopLevelArtifacts: TypeAlias = Mapping[ArtifactIdOrFilePath, TopLevelArtifactFlags]


class DvcYamlModel(DvcBaseModel):
    model_config = ConfigDict(title="dvc.yaml", extra="forbid")
    vars: Vars | None = Field(default=None, title="Variables")
    """List of values for substitution.\n\nMay include any dict or a path to a params file which may be a string or a dict to params in the file).\n\nUse elsewhere in `dvc.yaml` with the `${}` substitution expression."""
    stages: Mapping[StageName, Definition] | None = None
    """List of stages that form a pipeline."""
    plots: TopLevelPlots | TopLevelPlotsList | None = None
    """Top level plots definition."""
    params: Sequence[FilePath] | None = None
    """List of parameter files"""
    metrics: Sequence[FilePath] | None = None
    """List of metric files"""
    artifacts: TopLevelArtifacts | None = None
    """Top level artifacts definition."""
