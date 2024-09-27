"""Data columns model."""

from itertools import chain
from typing import Any, Self

from more_itertools import one
from pydantic import BaseModel, computed_field, model_validator

from boilercv_pipeline.models.column import Col, Kind, LinkedCol
from boilercv_pipeline.models.stage import DataStage

D = DataStage()


class Cols(BaseModel):
    """Columns."""

    def get_indices(self, *stages: str) -> list[Col]:
        """Get all index columns, optionally selecting by stage."""
        cols = get_cols(self, Kind.idx)
        if not stages:
            return cols
        return [
            c
            for c in cols
            if c in chain.from_iterable(get_cols(self, stage) for stage in stages)
        ]

    @property
    def index(self) -> Col:
        """Singular index column in a set of columns with one index."""
        return one(self.get_indices())

    @computed_field
    @property
    def sources(self) -> list[LinkedCol]:
        """All source columns."""
        return get_cols(self, D.src)

    @property
    def dests(self) -> list[Col]:
        """All destination columns."""
        return get_cols(self, D.dst)

    @model_validator(mode="after")
    def validate_unique(self) -> Self:
        """Validate columns are unique."""
        cols: list[str] = []
        for f, v in dict(self).items():
            if not self.model_fields[f].metadata:
                continue
            if isinstance(v, list):
                cols.extend([c() for c in v])
            else:
                cols.append(v())
        if len(cols) != len(s := set(cols)):
            raise ValueError(
                f"Columns must be unique. Duplicates: {[c for c in s if cols.count(c) > 1]}"
            )

        return self


def get_cols(cols_model: Cols, meta: str) -> list[Any]:
    """Get columns."""
    cols = dict(cols_model)
    return list(
        chain.from_iterable(
            cols[field] if isinstance(cols[field], list) else [cols[field]]
            for field, info in cols_model.model_fields.items()
            if meta in info.metadata
        )
    )
