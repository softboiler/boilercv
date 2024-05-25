"""Morphs."""

from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from re import sub
from typing import Any, Generic, Self, overload

from pydantic import BaseModel, Field
from tomlkit import parse
from tomlkit.container import Container
from tomlkit.items import Item

from boilercv.morphs import BaseMorph, M, Morph
from boilercv_pipeline import mappings
from boilercv_pipeline.types import (
    Ctx,
    CtxV,
    CtxV_T,
    Defaults,
    Expr,
    K,
    Leaf,
    Morphs,
    Node,
    Repl,
    V,
)


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


class CtxMorph(Morph[K, V], Generic[K, V]):
    """Context morph."""

    def model_post_init(self, ctx: Ctx | None = None) -> None:
        """Run post-initialization."""
        if not ctx:
            return
        all_morphs = self.get_morphs_from_ctx(Morphs, ctx)
        with self.thaw_self(validate=True):
            result = self
            for model, morphs in all_morphs.items():
                if not isinstance(result, model):
                    continue
                for morph, ctx_v in morphs:
                    result = self.pipe(morph, ctx_v)
            self.root = result

    @classmethod
    def get_morphs(cls) -> Morphs:
        """Get morphs."""
        return Morphs()

    @classmethod
    def get_morphs_from_ctx(cls, typ: type[CtxV_T], ctx) -> CtxV_T:
        """Get context value."""
        key = typ.name_to_snake()
        val = ctx.get(key)
        if not val:
            raise ValueError(f"{key} missing from context.")
        return val  # pyright: ignore[reportReturnType]

    @classmethod
    def with_ctx(cls, obj: Any, ctx: Ctx | None = None):
        """Validate."""
        return cls.model_validate(obj, context=ctx or Ctx())

    @classmethod
    def json_with_morphs(
        cls, json_data: str | bytes | bytearray, ctx: Ctx | None = None
    ):
        """Validate JSON."""
        return cls.model_validate_json(json_data, context=ctx or Ctx())


def set_defaults(i: CtxMorph[K, V], defaults: Defaults[K, V]) -> CtxMorph[K, V]:
    """Set `self.default_keys` using `self.default_factory` or `self.default`."""
    if not defaults.default_keys:
        return i
    if any(key not in i for key in defaults.default_keys):
        if defaults.default_factory:
            default = defaults.default_factory()
        elif defaults.default is not None:
            default = defaults.default
        else:
            default = i.get_inner_types()[1]()
        i.get_inner_types()[1]()
        return dict.fromkeys(defaults.default_keys, default) | i
    return i


def get_ctx(*ctx_vs: CtxV):
    """Compose a context."""
    return {ctx_v.name_to_snake(): ctx_v for ctx_v in ctx_vs}


@contextmanager
def context(ctx_morph: CtxMorph[Any, Any], *ctx_vs: CtxV, **kwds: Any) -> Iterator[Ctx]:
    """Pydantic context manager."""
    yield get_ctx(ctx_morph.get_morphs(**kwds), *ctx_vs)


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
