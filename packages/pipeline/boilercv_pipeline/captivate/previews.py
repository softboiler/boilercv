"""Image and video previews."""

import inspect
from collections.abc import Callable, Mapping, MutableSequence, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Literal, TypeAlias

from numpy import array, ceil, fliplr, issubdtype, ndarray, ones, pad, sqrt
from pandas import DataFrame
from pyqtgraph import (
    GraphicsLayoutWidget,
    ImageView,
    LineSegmentROI,
    PolyLineROI,
    TextItem,
    mkBrush,
    mkPen,
    mkQApp,
    setConfigOption,
)
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLayout, QPushButton
from ruamel.yaml import YAML

from boilercv.images import scale_bool
from boilercv.types import DA, ArrInt, Img
from boilercv_pipeline.captivate import FRAMERATE_CONT

YAML_INDENT = 2
yaml = YAML()
yaml.indent(mapping=YAML_INDENT, sequence=YAML_INDENT, offset=YAML_INDENT)
yaml.preserve_quotes = True


def init():
    """Initialize `boilercv.gui`."""
    setConfigOption("imageAxisOrder", "row-major")


Viewable: TypeAlias = Any  # The true type is a complex union of lots of array types
NamedViewable: TypeAlias = Mapping[str | int, Viewable]
MultipleViewable: TypeAlias = Sequence[Viewable]
MutableViewable: TypeAlias = MutableSequence[Viewable]
AllViewable: TypeAlias = Viewable | NamedViewable | MultipleViewable

# * -------------------------------------------------------------------------------- * #
# * IMAGE VIEWER

WINDOW_SIZE = (800, 600)
WINDOW_NAME = "Image viewer"
SMALLER_GRIDS = {
    1: (1, 1),
    2: (1, 2),
    3: (1, 3),
    4: (2, 2),
    5: (2, 3),
    6: (2, 3),
    7: (2, 4),
    8: (2, 4),
    9: (2, 5),
    10: (2, 5),
    11: (3, 4),
    12: (3, 4),
}
"""Rectangular grid sizes for up to twelve views. Use square grids beyond that."""


def view_images(images: AllViewable, name: str = "", framerate: int = FRAMERATE_CONT):
    """Compare multiple images or videos."""
    with image_viewer(images, name, framerate):
        pass


@contextmanager
def image_viewer(images: AllViewable, name: str = "", framerate: int = FRAMERATE_CONT):  # noqa: C901  # pyright: ignore[reportRedeclaration]
    """View and interact with images and video."""
    images: NamedViewable = coerce_images(images)
    num_views = len(images)
    shape = SMALLER_GRIDS.get(num_views, get_square_grid(num_views))
    height, width = shape
    coords = get_grid_coordinates(shape)
    image_views, app, window, layout, button_layout = make_window(name)

    def main():
        """Handle required setup and teardown."""
        add_image_views()
        add_actions()
        image_view_mapping = set_images(images, image_views)
        try:
            yield image_view_mapping, app, window, layout, button_layout
        finally:
            window.show()
            app.exec()

    def add_image_views():
        """Add image views in a grid."""
        for column in range(width):
            layout.setColumnStretch(column, 1)
        for coord in coords:
            image_view = get_image_view(framerate)
            layout.addWidget(image_view, *coord)
            image_views.append(image_view)

    def add_actions():
        """Add buttons and keypress events to the window."""
        window.key_signal.connect(keyPressEvent)
        layout.addLayout(button_layout, height, 0, 1, width)
        if num_views > 1:
            add_button(button_layout, "Toggle Play All", trigger_space).setFocus()
        add_button(button_layout, "Continue", app.quit)

    def trigger_space():
        """Trigger a spacebar keypress event. For propagating logic to image views."""
        keyPressEvent(
            QKeyEvent(
                QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier
            )
        )

    def keyPressEvent(ev: QKeyEvent):  # noqa: N802
        """Handle quit events and propagate keypresses to image views."""
        if ev.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Q, Qt.Key.Key_Enter):
            app.quit()
            ev.accept()
        for image_view in image_views:
            image_view.keyPressEvent(ev)

    yield from main()


# * -------------------------------------------------------------------------------- * #


def make_window(name: str = ""):
    """Start a PyQtGraph app and prepare an app window with a default layout."""
    # Isolate ImageView in a layout cell. It is complicated to directly modify the UI
    # of ImageView. Can't use the convenient LayoutWidget because
    # GraphicsLayoutWidget cannot contain it, and GraphicsLayoutWidget is convenient on
    # its own.
    app = mkQApp()
    image_views: list[ImageView] = []
    layout = QGridLayout()
    button_layout = QHBoxLayout()
    window = GraphicsLayoutWidgetWithKeySignal(size=WINDOW_SIZE)
    window.setLayout(layout)
    window.setWindowTitle(f"{WINDOW_NAME}: {name or get_calling_scope_name()}")
    return image_views, app, window, layout, button_layout


def get_grid_coordinates(shape: tuple[int, int]) -> list[tuple[int, int]]:
    """Get the coordinates of a grid."""
    (y, x) = ones(shape).nonzero()
    return list(zip(y, x, strict=True))


def get_square_grid(num_views: int) -> tuple[int, int]:
    """Get the dimensions of a square grid for the given number of views."""
    minimum_side_length = ceil(sqrt(num_views))
    side_length = int(minimum_side_length)
    (height, width) = (side_length,) * 2
    return height, width


def coerce_images(images: AllViewable) -> NamedViewable:
    """Coerce images to a mapping of title to image."""
    if isinstance(images, Mapping):
        images_ = images
    elif isinstance(images, ndarray | DA):
        images_ = [images]
    elif isinstance(images, Sequence):
        # If given a sequence that could be a video or a set of images/videos to
        # compare, assume it is a video if it is too long to be a set of comparisons.
        largest_grid = 16
        images_ = [array(pad_images(images))] if len(images) > largest_grid else images
    else:
        raise TypeError(f"Unsupported type for images: {type(images)}")

    return (
        {title: array(pad_images(viewable)) for title, viewable in images_.items()}
        if isinstance(images_, Mapping)
        else {i: array(pad_images(viewable)) for i, viewable in enumerate(images_)}
    )


def pad_images(images: MultipleViewable) -> MutableViewable:  # pyright: ignore[reportRedeclaration]
    """Pad images to a common size and pack into an array."""
    flat_image = isinstance(images, ndarray | DA) and (
        # One-channel
        images.ndim == 2
        # Up to four-channel
        or (images.ndim == 3 and images.shape[-1] <= 4)
    )
    images: MutableViewable = [images] if flat_image else list(images)
    shapes = DataFrame(
        columns=["height", "width"], data=list({image.shape[:2] for image in images})
    ).set_index(["height", "width"], drop=False)
    if len(shapes) == 1:
        return images
    # Subtract shape from largest shape and split the pad evenly
    pads = (
        (shapes[["height", "width"]].max() - shapes[["height", "width"]]) // 2
    ).set_axis(axis="columns", labels=["hpad", "wpad"])
    for i, image in enumerate(images):
        this_pad: tuple[int, int] = tuple(pads.loc[image.shape[:2], :])  # pyright: ignore[reportArgumentType, reportAssignmentType]
        hpad, wpad = this_pad
        zero_pad_for_additional_dims = ((0, 0),) * (image.ndim - 2)
        # If a pad is odd, add an extra to the right/top of the pad
        pad_width = (
            (hpad, hpad + hpad % 2),
            (wpad, wpad + wpad % 2),
            *zero_pad_for_additional_dims,
        )
        images[i] = pad(image, pad_width)
    return images


def set_images(
    images: NamedViewable, image_views: list[ImageView]
) -> dict[str | int, ImageView]:
    """Set images into the image views."""
    for (title, viewable), image_view in zip(images.items(), image_views, strict=False):
        if issubdtype(viewable.dtype, bool):
            viewable = scale_bool(viewable)
        image_view.setImage(viewable.squeeze())
        if isinstance(title, str):
            image_view.addItem(TextItem(title, fill=mkBrush("black")))
    return dict(zip(images.keys(), image_views, strict=False))


class GraphicsLayoutWidgetWithKeySignal(GraphicsLayoutWidget):
    """Emit key signals on `key_signal`."""

    key_signal = Signal(QKeyEvent)

    def keyPressEvent(self, ev: QKeyEvent):  # noqa: N802
        """Handle keypresses."""
        super().keyPressEvent(ev)
        self.key_signal.emit(ev)


def add_button(layout: QLayout, label: str, func: Callable[..., Any]) -> QPushButton:
    """Add a named button to a layout and connect it to a callback."""
    button = QPushButton(label)
    button.clicked.connect(func)
    layout.addWidget(button)
    return button


def get_image_view(framerate: int = FRAMERATE_CONT) -> ImageView:
    """Get an image view suitable for previewing images."""
    image_view = ImageView()
    image_view.playRate = framerate
    image_view.ui.histogram.hide()
    image_view.ui.roiBtn.hide()
    image_view.ui.menuBtn.hide()
    return image_view


def get_calling_scope_name():
    """Get the name of the calling scope."""
    current_frame = inspect.currentframe()
    scope_name = current_frame.f_back.f_code.co_name  # pyright: ignore[reportOptionalMemberAccess]
    while scope_name in {
        "image_viewer",
        "view_images",
        "preview_images",
        "make_window",
        "__enter__",
        "eval_in_context",
        "evaluate_expression",
        "_run_with_interrupt_thread",
        "_run_with_unblock_threads",
        "new_func",
        "internal_evaluate_expression_json",
        "do_it",
        "process_internal_commands",
    }:
        current_frame = current_frame.f_back  # pyright: ignore[reportOptionalMemberAccess]
        scope_name = current_frame.f_back.f_code.co_name  # pyright: ignore[reportOptionalMemberAccess]
    return scope_name


# * -------------------------------------------------------------------------------- * #


def save_roi(roi_vertices: ArrInt, roi_path: Path):
    """Save an ROI represented by an ordered array of vertices."""
    yaml.dump(roi_vertices.tolist(), roi_path)


def edit_roi(
    image: ArrInt, roi_path: Path, roi_type: Literal["poly", "line"] = "poly"
) -> ArrInt:
    """Edit the region of interest for an image."""
    with image_viewer(image) as (image_views, _app, window, _layout, button_layout):
        common_roi_args = dict(
            pen=mkPen("red"),
            hoverPen=mkPen("magenta"),
            handlePen=mkPen("blue"),
            handleHoverPen=mkPen("magenta"),
            positions=fliplr(load_roi(image, roi_path, roi_type)),
        )
        roi = (
            PolyLineROI(**common_roi_args, closed=True)
            if roi_type == "poly"
            else LineSegmentROI(**common_roi_args)
        )

        def main():
            """Allow ROI interaction."""
            window.key_signal.connect(keyPressEvent)
            button = QPushButton("Save ROI")
            button.clicked.connect(save_roi_)
            button_layout.addWidget(button)
            image_views[0].addItem(roi)

        def keyPressEvent(ev: QKeyEvent):  # noqa: N802
            """Save ROI or quit on key presses."""
            if ev.key() == Qt.Key.Key_S:
                save_roi_()
                ev.accept()

        def save_roi_():
            """Save the ROI."""
            vertices = get_roi_vertices()
            save_roi(vertices, roi_path)

        def get_roi_vertices() -> ArrInt:
            """Get the vertices of the ROI."""
            return fliplr(array(roi.saveState()["points"], dtype=int))

        main()

    return get_roi_vertices()


def load_roi(
    img: Img, roi_path: Path, roi_type: Literal["poly", "line"] = "poly"
) -> ArrInt:
    """Load the region of interest for an image."""
    (width, height) = img.shape[-2:]
    if roi_path.exists():
        vertices: list[tuple[int, int]] = yaml.load(
            roi_path.read_text(encoding="utf-8")
        )
    else:
        vertices = (
            [(0, 0), (0, width), (height, width), (height, 0)]
            if roi_type == "poly"
            else [(0, 0), (height, width)]
        )
    return array(vertices, dtype=int)


# * -------------------------------------------------------------------------------- * #

init()
