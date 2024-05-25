"""Morphs."""

from collections import UserDict, defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from re import sub
from typing import Any, ClassVar, Generic, NamedTuple, Self, overload

from pydantic import BaseModel, Field
from tomlkit import parse
from tomlkit.container import Container
from tomlkit.items import Item

from boilercv.morphs import BaseMorph, M, Morph
from boilercv_pipeline import mappings
from boilercv_pipeline.annotations import CV, SK, CtxV, Expr, Symbol
from boilercv_pipeline.types import Ctx, K, Leaf, Node, T, V

# * MARK: Pydantic models


class Solutions(BaseModel):
    """Solutions for a symbol."""

    solutions: list[Expr] = Field(default_factory=list)
    """Solutions."""
    warnings: list[str] = Field(default_factory=list)
    """Warnings."""


# * MARK: Classes for morph pipelines


class Repl(NamedTuple, Generic[T]):
    """Contents of `dst` to replace with `src`, with `find` substrings replaced with `repl`."""

    src: T
    """Source identifier."""
    dst: T
    """Destination identifier."""
    find: str
    """Find this in the source."""
    repl: str
    """Replacement for what was found."""


# * MARK: Context value handlers


def get_ctx(*ctx_vs: CtxV):
    """Compose a context."""
    return {ctx_v.name_to_snake(): ctx_v for ctx_v in ctx_vs}


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


class LocalSymbols(UserDict[SK, Symbol], CtxV, Generic[SK]):
    """Local symbols."""


@dataclass
class Defaults(CtxV, Generic[K, V]):
    """Context for expression validation."""

    default_keys: tuple[K, ...] = field(default_factory=tuple)
    """Default keys."""
    default: V | None = None
    """Default value."""
    default_factory: Callable[..., Any] | None = None
    """Default value factory."""


# * MARK: Hybrid context value and context morph handlers


@dataclass
class Pipe(Generic[T]):
    """Pipe."""

    f: Callable[[T, Any], T]
    ctx_v: CtxV


class Morphs(UserDict["type[CtxMorph[Any, Any]]", list[Pipe[Any]]], CtxV):
    """Pipes."""

    def __or__(self, other: Any) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(other, Morphs):
            merged: dict[type[CtxMorph[Any, Any]], list[Pipe[Any]]] = defaultdict(list)
            for model, pipes in other.items():
                merged[model].extend(pipes)
            return type(self)(merged)
        return NotImplemented


def merge_morphs(*all_morphs: Morphs) -> Morphs:
    """Merge morphs."""
    merged: dict[type[CtxMorph[Any, Any]], list[Pipe[Any]]] = defaultdict(list)
    for morphs in all_morphs:
        for model, pipes in morphs.items():
            merged[model].extend(pipes)
    return Morphs(merged)


# * MARK: Context morphs


class CtxMorph(Morph[K, V], Generic[K, V]):
    """Context morph."""

    ctx: ClassVar[Ctx] = Ctx()
    """Context."""

    def model_post_init(self, ctx: Ctx | None = None) -> None:
        """Morph the model after initialization."""
        ctx = ctx or self.ctx
        morphs = self.get_context_value(Morphs, ctx)
        with self.thaw_self(validate=True):
            result = self
            for model, pipes in morphs.items():
                if not isinstance(result, model):
                    continue
                for pipe in pipes:
                    result = self.pipe(pipe.f, pipe.ctx_v)
            self.root = result

    @classmethod
    def get_context_value(cls, typ: type[CV], ctx: Ctx | None) -> CV:
        """Get context values for a type."""
        key = typ.name_to_snake()
        val = (ctx or cls.ctx).get(key)
        if val is None:
            raise ValueError(f"{key} missing from context.")
        return val  # pyright: ignore[reportReturnType]

    @classmethod
    def with_ctx(cls, obj: Any, ctx: Ctx | None = None):
        """Validate."""
        return cls.model_validate(obj, context=ctx or cls.ctx)

    @classmethod
    def json_with_morphs(
        cls, json_data: str | bytes | bytearray, ctx: Ctx | None = None
    ):
        """Validate JSON."""
        return cls.model_validate_json(json_data, context=ctx or cls.ctx)

    @classmethod
    def set_defaults(
        cls,
        keys: tuple[K, ...] | None,
        value: V | None = None,
        factory: Callable[..., Any] | None = None,
    ) -> Morphs:
        """Set defaults."""
        keys = keys or ()
        return Morphs({cls: [Pipe(set_defaults, Defaults(keys, value, factory))]})


# * MARK: Context morph handlers


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


# TODO: Consider removing this


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
