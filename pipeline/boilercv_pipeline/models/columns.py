"""Data columns model."""

from itertools import chain
from typing import Any

from more_itertools import one
from pydantic import BaseModel, computed_field

from boilercv_pipeline.models.column import Col, Kind, LinkedCol
from boilercv_pipeline.models.stage import DataStage


class Cols(BaseModel):
    """Columns."""

    @property
    def index(self) -> Col:
        """Get the singular index column."""
        return one(self.indices)

    @property
    def indices(self) -> list[Col]:
        """All index columns."""
        return get_cols(self, Kind.idx)

    @computed_field
    @property
    def sources(self) -> list[LinkedCol]:
        """All source columns."""
        return get_cols(self, DataStage.src)

    @property
    def dests(self) -> list[Col]:
        """All destination columns."""
        return get_cols(self, DataStage.dst)


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
