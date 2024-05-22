"""Morphs."""

from collections.abc import Iterable, MutableMapping
from pathlib import Path
from re import sub
from typing import Any, ClassVar, Generic, Self, TypeVar, overload

from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticUndefinedType
from tomlkit import parse
from tomlkit.container import Container
from tomlkit.items import Item

from boilercv.morphs import BaseMorph, Morph
from boilercv_pipeline.correlations.dimensionless_bubble_diameter.types import Locals
from boilercv_pipeline.correlations.types import FormsRepl, Kind, kinds
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
    def set_defaults(cls, data: dict[K, V]) -> Self | dict[K, V]:
        """Set `self.default_keys` using `self.default_factory` or `self.default`."""
        if not cls.default_keys:
            return data
        if isinstance(data, PydanticUndefinedType) or any(
            key not in data for key in cls.default_keys
        ):
            return dict.fromkeys(  # pyright: ignore[reportReturnType]  # Eventually valid
                cls.default_keys,
                cls.default_factory() if cls.default_factory else cls.default,
            ) | ({} if isinstance(data, PydanticUndefinedType) else data)
        return data


class Forms(DefaultMorph[Kind, str]):
    """Forms."""

    default_keys: ClassVar = kinds
    default: ClassVar = ""


DefaultMorph.register(Forms)

T = TypeVar("T", bound=Expr)


class Soln(BaseModel, Generic[T]):
    """All solutions."""

    solutions: list[T] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def set_equation_forms(i: Forms, symbols: Locals) -> Forms:
    """Set equation forms."""
    return i.pipe(
        replace,
        (
            FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
            for find, repl in {"{o}": "0", "{bo}": "b0"}.items()
        ),
    ).pipe(
        regex_replace,
        (
            FormsRepl(src="sympy", dst="sympy", find=find, repl=repl)
            for sym in symbols
            for find, repl in {
                # ? Symbol split by `(` after first character.
                rf"{sym[0]}\*\({sym[1:]}([^)]+)\)": rf"{sym}\g<1>",
                # ? Symbol split by a `*` after first character.
                rf"{sym[0]}\*{sym[1:]}": rf"{sym}",
                # ? Symbol missing `*` resulting in failed attempt to call it
                rf"{sym}\(": rf"{sym}*(",
            }.items()
        ),
    )


class TomlMorph(BaseMorph[K, V], Generic[K, V]):
    """Morphable mapping."""

    path: Path
    root: Morph[K, V] = Field(default_factory=Morph[K, V])

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
            model_dump: Node = self.root.model_dump(mode="json")
            src = model_dump
        dst = dst or parse(self.path.read_text("utf-8"))
        if not isinstance(dst, MutableMapping):
            return
        for key in [k for k in dst if k not in src]:
            del dst[key]
        for key in src:
            if key in dst:
                if src[key] == dst[key]:
                    continue
                if isinstance(src[key], dict) and isinstance(dst[key], MutableMapping):
                    self.sync(src[key], dst[key])
                    continue
            dst[key] = src[key]
        return dst

    def write(self) -> None:
        """Write to TOML."""
        self.path.write_text(self.sync().as_string(), "utf-8")

    @classmethod
    def read(cls, path: Path) -> Self:
        """Read from TOML."""
        return cls(path=path, root=parse(path.read_text("utf-8")))  # type: ignore[reportArgumentType]
