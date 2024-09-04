"""Data columns model."""

from itertools import chain

from pydantic import BaseModel

from boilercv_pipeline.models.column import Col, Kind
from boilercv_pipeline.models.stage import DataStage


class Cols(BaseModel):
    """Columns."""

    @property
    def idx(self) -> list[Col]:
        """All index columns."""
        return get_cols(self, Kind.idx)

    @property
    def sources(self) -> list[Col]:
        """All source columns."""
        return get_cols(self, DataStage.src)

    @property
    def dests(self) -> list[Col]:
        """All destination columns."""
        return get_cols(self, DataStage.dst)


def get_cols(cols_model: Cols, meta: str) -> list[Col]:
    """Get columns."""
    cols = dict(cols_model)
    return list(
        chain.from_iterable(
            cols[field] if isinstance(cols[field], list) else [cols[field]]
            for field, info in cols_model.model_fields.items()
            if meta in info.metadata
        )
    )
