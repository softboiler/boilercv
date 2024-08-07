"""Config."""

from functools import cached_property

from boilercv_pipeline.models import Params


class Settings:
    """Settings."""

    @cached_property
    def params(self) -> Params:
        """Parameters."""
        return Params()


default = Settings()
