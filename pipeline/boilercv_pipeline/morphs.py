"""Morphs."""

from collections.abc import Iterable
from pathlib import Path
from re import sub
from typing import Any, ClassVar, Generic, Self, overload

from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticUndefinedType
from tomlkit import parse
from tomlkit.container import Container
from tomlkit.items import Item

from boilercv.morphs import BaseMorph, M, Morph
from boilercv_pipeline import mappings
from boilercv_pipeline.types import Expr, K, Leaf, Node, Repl, V


def replace(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
    """Make replacements from `Repl`s."""
    for r in repls:
        i[r.dst] = i[r.src].replace(r.find, r.repl)
    return i


def regex_replace(i: dict[K, str], repls: Iterable[Repl[K]]) -> dict[K, str]:
    """Make regex replacements."""
    for r in repls:
        i[r.dst] = sub(r.find, r.repl, i[r.src])
    return i


class DefaultMorph(Morph[K, V], Generic[K, V]):
    """Morph with default values."""

    default_keys: ClassVar[tuple[Any, ...]] = ()
    """Default keys."""
    default: ClassVar = None
    """Default value."""
    default_factory: ClassVar = None
    """Default value factory."""

    @model_validator(mode="before")
    @classmethod
    def set_defaults(cls, data: dict[K, V]) -> dict[K, V]:
        """Set `self.default_keys` using `self.default_factory` or `self.default`."""
        if not cls.default_keys:
            return data
        if isinstance(data, PydanticUndefinedType) or any(
            key not in data for key in cls.default_keys
        ):
            if cls.default_factory:
                default = cls.default_factory()
            elif cls.default is not None:
                default = cls.default
            else:
                default = cls.get_inner_types()[1]()
            cls.get_inner_types()[1]()
            return dict.fromkeys(  # pyright: ignore[reportReturnType]  # Eventually valid
                cls.default_keys, default
            ) | ({} if isinstance(data, PydanticUndefinedType) else data)
        return data

    def model_post_init(self, context: Any) -> None:
        """Run post-initialization recursievely."""
        for key in self.keys():
            if isinstance(key, DefaultMorph):
                key.model_post_init(context)
        for value in self.values():
            if isinstance(value, DefaultMorph):
                value.model_post_init(context)


class Solutions(BaseModel):
    """Solutions for a symbol."""

    solutions: list[Expr] = Field(default_factory=list)
    """Solutions."""
    warnings: list[str] = Field(default_factory=list)
    """Warnings."""


class TomlMorph(BaseMorph[M], Generic[M]):
    """Morphable mapping."""

    path: Path
    root: M

    def model_dump(self, *args, **kwds):
        """Dump {attr}`root` instead of {class}`TomlMorph` itself."""
        return self.root.model_dump(*args, **kwds)

    def model_dump_json(self, *args, **kwds):
        """Dump {attr}`root` instead of {class}`TomlMorph` itself."""
        return self.root.model_dump_json(*args, **kwds)

    # ! Root case
    @overload
    def sync(self, src: None = None, dst: None = None) -> Container: ...
    # ! General case
    @overload
    def sync(self, src: Node | Leaf, dst: Item | Container) -> None: ...
    # ! Union
    def sync(
        self, src: Node | Leaf | None = None, dst: Item | Container | None = None
    ) -> Container | None:
        """Sync a TOML document."""
        if not src:
            model_dump: Node = self.model_dump(mode="json")
            src = model_dump
        dst = dst or parse(self.path.read_text("utf-8"))
        return mappings.sync(src, dst)

    def write(self) -> None:
        """Write to TOML."""
        self.path.write_text(self.sync().as_string(), "utf-8")

    @classmethod
    def read(cls, path: Path) -> Self:
        """Read from TOML."""
        return cls(path=path, root=parse(path.read_text("utf-8")))  # type: ignore[reportArgumentType]
