"""Notebooks."""

from pydantic import BaseModel, ConfigDict


class Notebooks(BaseModel):
    """Notebook settings."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    time: str = "2024-07-18T17:44:35"
    """Example trial timestamp."""
    scale: float = 1.6
    """Plot scale."""
    marker_scale: float = 20
    """Marker scale."""

    @property
    def size(self) -> float:
        """Marker size."""
        return self.scale * self.marker_scale

    @property
    def font_scale(self) -> float:
        """Font scale."""
        return self.scale

    frame_step: int = 100
    """Frame step size."""
    num_frames: int = 8
    """Last frame to analyze."""

    @property
    def frames(self) -> slice:
        """Frames.

        A list that will become a slice. Not a tuple because `ploomber_engine` can't inject
        tuples. Automatically scale the frame to stop at by the step size.
        """
        return slice(*[None, *[self.frame_step * f for f in (self.num_frames - 1, 1)]])
