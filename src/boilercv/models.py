"""Models."""

from types import NoneType
from typing import get_args

from pydantic import BaseModel, SerializerFunctionWrapHandler, model_serializer


class BaseModelDefaultAsNone(BaseModel):
    """Avoid serializing defaults."""

    @model_serializer(mode="wrap")
    def serialize_default_as_none(self, nxt: SerializerFunctionWrapHandler) -> str:
        """Serialize defaults as `None`."""
        for (field, value), info in zip(
            dict(self).items(), self.model_fields.values(), strict=True
        ):
            if (
                value is not None
                and value == info.default
                and (ann := info.annotation)
                and NoneType in get_args(ann)
            ):
                setattr(self, field, None)
        return nxt(self)
