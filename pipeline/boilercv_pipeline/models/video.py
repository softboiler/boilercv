"""Video model."""

from pydantic import BaseModel

from boilercv.data import PX, X, Y
from boilercv_pipeline.models.column import Col


class VideoDims(BaseModel):
    """Video dimensions."""

    y: Col = Col(Y, unit=PX)
    x: Col = Col(X, unit=PX)
