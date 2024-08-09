"""Config."""

from functools import cached_property

from boilercv_pipeline.models import Params, Paths


class Settings:
    """Settings."""

    @cached_property
    def params(self) -> Params:
        """Parameters."""
        return Params()

    @cached_property
    def paths(self) -> Paths:
        """Parameters."""
        return self.params.paths


default = Settings()
