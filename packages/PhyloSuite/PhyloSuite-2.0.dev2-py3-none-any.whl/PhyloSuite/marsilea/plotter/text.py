# from __future__ import annotations

from itertools import zip_longest

from numbers import Number

import matplotlib.pyplot as plt
import numpy as np
import warnings
from dataclasses import dataclass
from matplotlib.axes import Axes
from matplotlib.colors import is_color_like
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from typing import List, Iterable

from .base import RenderPlan
from ..utils import pairwise, relative_luminance


class Segment:
    """
    The total length is unchanged
    """

    up: float
    low: float

    # limit
    max: float = None
    min: float = None

    def __repr__(self):
        return f"Segments({self.label}: {self.low:.2f} - {self.up:.2f})"

    def __init__(self, low, up, label=""):
        self.low = low
        self.up = up
        self._length = up - low

        self.side = None
        self.label = label

    @property
    def length(self):
        return self._length

    @property
    def mid(self):
        return self.length / 2 + self.low

    def overlap(self, other):
        # Other on the right or left
        if self.low >= other.up or other.low >= self.up:
            return False
        else:
            return True

    def set_lim(self, lim):
        if lim.length < self.length:
            raise ValueError("Length of the limit is too short")
        self.max = lim.up
        self.min = lim.low
        # If lower than the lim
        if self.low < self.min:
            self.low = self.min
            self.up = self.low + self.length
        # If upper than the lim
        if self.up > self.max:
            self.up = self.max
            self.low = self.up - self.length

    def move_up(self, offset):
        # check if move across lim
        final_up = self.up + offset
        if final_up <= self.max:
            self.set_up(final_up)
        else:
            self.set_up(self.max)

    def move_down(self, offset):
        # check if move across lim
        final_low = self.low - offset
        if final_low >= self.min:
            self.set_low(final_low)
        else:
            self.set_low(self.min)

    def set_up(self, up):
        if up <= self.max:
            final_low = up - self.length
            if final_low >= self.min:
                self.low = final_low
                self.up = up

    def set_low(self, low):
        if low >= self.min:
            final_up = low + self.length
            if final_up <= self.max:
                self.low = low
                self.up = final_up


def adjust_segments(lim: Segment, segments: List[Segment]):
    """Assume the segments is ascending"""
    # Check the order
    sl = []
    for s in segments:
        sl.append(s.length)
        s.set_lim(lim)

    segments_length = np.sum(sl)
    space = lim.length
    if segments_length > space:
        warnings.warn(
            "No enough space to place all labels, " "try reducing the fontsize."
        )

    segments_length_r = segments_length
    space_r = space

    for ix, (s1, s2) in enumerate(pairwise(segments)):
        if ix == 0:
            distance = s1.low - lim.low
            offset = segments_length - (space - distance)
            if offset > 0:
                if offset > distance:
                    s1.set_low(lim.low)
                else:
                    s1.move_down(offset)

        space -= s1.length
        segments_length -= s1.length
        if s1.overlap(s2) or s2.up < s1.low:
            # if overlapped, make s2 next to s1
            s2.set_low(s1.up)
        else:
            # space between s1 and s2
            distance = s2.low - s1.up

            offset = segments_length - (space - distance)
            # if what's left is not enough to place remaining
            # The total segments is longer than remain space
            if offset > 0:
                # This means no enough space
                # We could only overlay them
                if offset > distance:
                    s2.set_low(s1.up)
                else:
                    s2.move_down(offset)

    for ix, (s1, s2) in enumerate(pairwise(segments[::-1])):
        if ix == 0:
            distance = s1.up - lim.up
            offset = segments_length_r - (space_r - distance)
            if offset > 0:
                if offset > distance:
                    s1.set_up(lim.up)
                else:
                    s1.move_up(offset)

        space_r -= s1.length
        segments_length_r -= s1.length
        if s1.overlap(s2) or s2.low > s1.up:
            # if overlapped, make s2 next to s1
            s2.set_up(s1.low)
        else:
            # space between s1 and s2
            distance = s2.low - s1.up

            offset = segments_length_r - (space_r - distance)
            # if what's left is not enough to place remaining
            # The total segments is longer than remain space
            if offset > 0:
                # This means no enough space
                # We could only overlay them
                if offset > distance:
                    s2.set_up(s1.low)
                else:
                    s2.move_up(offset)


# For debug purpose
def plot_segments(segments, lim=None):
    ys = []
    xmin = []
    xmax = []
    for ix, s in enumerate(segments):
        ys.append(ix % 2 + 1)
        xmin.append(s.low)
        xmax.append(s.up)

    _, ax = plt.subplots()

    if lim is not None:
        # Draw the lim
        ax.axhline(y=0, xmin=lim.low, xmax=lim.up, color="black")
        ax.axvline(x=lim.low, color="black", linestyle="dashed")
        ax.axvline(x=lim.up, color="black", linestyle="dashed")

    ax.hlines(ys, xmin, xmax)
    ax.set_ylim(-0.5, 5)


class AdjustableText:
    def __init__(
        self,
        x,
        y,
        text,
        ax=None,
        renderer=None,
        pointer=None,
        expand=(1.05, 1.05),
        va=None,
        ha=None,
        rotation=None,
        connectionstyle=None,
        relpos=None,
        linewidth=None,
        **kwargs,
    ):
        if ax is None:
            ax = plt.gca()
        if renderer is None:
            fig = plt.gcf()
            renderer = fig.canvas.get_renderer()
        self.ax = ax
        self.renderer = renderer
        if pointer is None:
            pointer = (x, y)
        self.pointer = pointer
        self.x = x
        self.y = y
        self.text = text

        self.va = va
        self.ha = ha
        self.rotation = rotation
        self.connectionstyle = connectionstyle
        self.relpos = relpos
        self.linewidth = linewidth
        self.text_obj = Text(
            x,
            y,
            text,
            va=va,
            ha=ha,
            rotation=rotation,
            transform=self.ax.transAxes,
            **kwargs,
        )
        self.text_options = kwargs
        ax.add_artist(self.text_obj)
        self._bbox = self.text_obj.get_window_extent(self.renderer).expanded(*expand)
        self.annotation = None

    def get_display_coordinate(self):
        return self.text_obj.get_transform().transform((self.x, self.y))

    def get_bbox(self):
        return self._bbox

    def get_segment_x(self):
        return Segment(self._bbox.xmin, self._bbox.xmax, label=self.text)

    def get_segment_y(self):
        return Segment(self._bbox.ymin, self._bbox.ymax, label=self.text)

    def set_display_coordinate(self, tx, ty):
        x, y = self.ax.transAxes.inverted().transform((tx, ty))
        self.x = x
        self.y = y

    def set_display_x(self, tx):
        x, _ = self.ax.transAxes.inverted().transform((tx, 0))
        self.x = x

    def set_display_y(self, ty):
        _, y = self.ax.transAxes.inverted().transform((0, ty))
        self.y = y

    def redraw(self):
        self.text_obj.set_position((self.x, self.y))

    def draw_annotate(self):
        self.text_obj.remove()
        self.annotation = self.ax.annotate(
            self.text,
            xy=self.pointer,
            xytext=(self.x, self.y),
            va=self.va,
            ha=self.ha,
            rotation=self.rotation,
            transform=self.ax.transAxes,
            arrowprops=dict(
                arrowstyle="-",
                connectionstyle=self.connectionstyle,
                linewidth=self.linewidth,
                relpos=self.relpos,
            ),
            **self.text_options,
        )


# A container class for store arbitrary text params
class TextParams:
    _ha: str
    _va: str
    rotation = 0

    def __init__(self, **params):
        self._params = {}
        self.update_params(params)

    def update_params(self, params):
        for k, v in params.items():
            if k in ["ha", "horizontalalignment"]:
                self._ha = v
            elif k in ["va", "verticalalignment"]:
                self._va = v
            else:
                self._params[k] = v

    def to_dict(self):
        p = dict(va=self._va, ha=self._ha, rotation=self.rotation)
        p.update(self._params)
        return p


class _LabelBase(RenderPlan):
    texts = None
    is_flex = True
    texts_size = None
    padding = 0
    text_pad = 0
    text_gap = 0

    def __init__(self):
        # Params hard set by user
        self._user_params = {}

    def _sort_params(self, **params):
        for k, v in params.items():
            if v is not None:
                self._user_params[k] = v

    def get_text_params(self) -> TextParams:
        raise NotImplementedError

    @staticmethod
    def get_axes_coords(labels):
        coords = []
        use = False
        for i, c in enumerate(np.linspace(0, 1, len(labels) * 2 + 1)):
            if use:
                coords.append(c)
            use = not use
        return coords

    @staticmethod
    def get_text_color(bgcolor):
        """Get text color by background color"""
        lum = relative_luminance(bgcolor)
        return ".15" if lum > 0.408 else "w"

    def get_expand(self):
        if self.is_flank:
            return 1.0 + self.text_pad, 1.0 + self.text_gap
        else:
            return 1.0 + self.text_gap, 1.0 + self.text_pad

    def silent_render(self, figure, expand=(1.0, 1.0)):
        renderer = figure.canvas.get_renderer()
        ax = figure.add_axes([0, 0, 1, 1])
        params = self.get_text_params()

        locs = self.get_axes_coords(self.texts)
        sizes = []
        for s, c in zip(self.texts, locs):
            x, y = (0, c) if self.is_flank else (c, 0)
            t = ax.text(x, y, s=s, transform=ax.transAxes, **params.to_dict())
            bbox = t.get_window_extent(renderer).expanded(*expand)
            if self.is_flank:
                sizes.append(bbox.xmax - bbox.xmin)
            else:
                sizes.append(bbox.ymax - bbox.ymin)

        ax.remove()
        return np.max(sizes) / figure.get_dpi()

    def get_canvas_size(self, figure, **kwargs):
        self.texts_size = self.silent_render(figure, expand=self.get_expand())
        return self.texts_size + self.padding / 72


@dataclass
class AnnoTextConfig:
    va: str
    ha: str
    rotation: int
    relpos: tuple

    angleA: int
    angleB: int
    armA: int = 10
    armB: int = 10

    def get_connectionstyle(self, armA=None, armB=None):
        armA = self.armA if armA is None else armA
        armB = self.armB if armB is None else armB
        return (
            f"arc,angleA={self.angleA},"
            f"angleB={self.angleB},"
            f"armA={armA},"
            f"armB={armB},"
            f"rad=0"
        )


anno_default_params = {
    "top": AnnoTextConfig(
        va="bottom", ha="center", rotation=90, angleA=-90, angleB=90, relpos=(0.5, 0)
    ),
    "bottom": AnnoTextConfig(
        va="top", ha="center", rotation=-90, angleA=90, angleB=-90, relpos=(0.5, 1)
    ),
    "right": AnnoTextConfig(
        va="center", ha="left", rotation=0, angleA=-180, angleB=0, relpos=(0, 0.5)
    ),
    "left": AnnoTextConfig(
        va="center", ha="right", rotation=0, angleA=0, angleB=-180, relpos=(1, 0.5)
    ),
}


class AnnoLabels(_LabelBase):
    """Annotate a few rows or columns

    This is useful when your heatmap contains many rows/columns,
    and you only want to annotate a few of them.

    Parameters
    ----------
    labels : list, np.ma.MaskedArray
        The length of the labels should match the main canvas side where
        it attaches to, the labels that won't be displayed should be masked.
    mark : list
        If your labels is not a mask array, this will help you mark the labels
        that you want to draw
    side : str
    text_pad : float
        Add extra space and the start and end of the label
    text_gap : float
        Add extra spacing between the labels, relative to the fontsize
    pointer_size : float
        The size of the pointer in inches
    linewidth : float
        The linewidth of the pointer
    connectionstyle :
    relpos : 2-tuple
    armA, armB : float
    label : str
        The label of the plot
    label_loc : {'top', 'bottom', 'left', 'right'}
        The location of the label
    label_props : dict
        The label properties
    options :
        Pass to :class:`matplotlib.text.Text`


    Examples
    --------

    .. plot::
        :context: close-figs

        >>> labels = np.arange(100)

        >>> import marsilea as ma
        >>> from marsilea.plotter import AnnoLabels
        >>> matrix = np.random.randn(100, 10)
        >>> h = ma.Heatmap(matrix)
        >>> marks = AnnoLabels(labels, mark=[3, 4, 5, 96, 97, 98])
        >>> h.add_right(marks)
        >>> h.render()

    """

    def __init__(
        self,
        labels,
        mark=None,
        text_pad=0.5,
        text_gap=0.5,
        pointer_size=0.5,
        linewidth=None,
        connectionstyle=None,
        relpos=None,
        armA=None,
        armB=None,
        label=None,
        label_loc=None,
        label_props=None,
        **options,
    ):
        if not np.ma.isMaskedArray(labels):
            if mark is not None:
                labels = np.ma.masked_where(~np.in1d(labels, mark), labels)
            else:
                raise TypeError(
                    "Must be numpy masked array or "
                    "use `marks` to mark "
                    "the labels you want to draw"
                )
        texts = self.data_validator(labels, target="1d")
        self.set_data(texts)
        self.texts = texts

        self.pointer_size = pointer_size
        self.linewidth = linewidth
        self.text_anchor = 0.4
        self.text_gap = text_gap
        self.text_pad = text_pad
        self.armA = armA
        self.armB = armB
        self.relpos = relpos
        self.connectionstyle = connectionstyle

        super().__init__()
        self._sort_params(**options)
        self.set_label(label, label_loc, label_props)

    def get_text_params(self):
        default_params = anno_default_params[self.side]
        self.relpos = default_params.relpos
        self.connectionstyle = default_params.get_connectionstyle(
            armA=self.armA, armB=self.armB
        )
        params = dict(
            va=default_params.va, ha=default_params.ha, rotation=default_params.rotation
        )
        p = TextParams(**params)
        p.update_params(self._user_params)
        return p

    def get_canvas_size(self, figure, **kwargs):
        expand = self.get_expand()
        canvas_size = self.silent_render(figure, expand)
        size = canvas_size + self.pointer_size
        self.text_anchor = self.pointer_size / size
        return size

    def render_ax(self, spec):
        ax = spec.ax
        labels = spec.data

        renderer = ax.get_figure().canvas.get_renderer()
        locs = self.get_axes_coords(labels)

        ax_bbox = ax.get_window_extent(renderer)
        params = self.get_text_params()

        text_options = dict(
            ax=ax,
            renderer=renderer,
            expand=self.get_expand(),
            linewidth=self.linewidth,
            relpos=self.relpos,
            connectionstyle=self.connectionstyle,
            **params.to_dict(),
        )

        texts = []
        segments = []
        if self.is_body:
            y = self.text_anchor
            for x, s in zip(locs, labels):
                if not np.ma.is_masked(s):
                    t = AdjustableText(x=x, y=y, text=s, pointer=(x, 0), **text_options)
                    texts.append(t)
                    segments.append(t.get_segment_x())

            lim = Segment(ax_bbox.xmin, ax_bbox.xmax)
            adjust_segments(lim, segments)
            for t, s in zip(texts, segments):
                t.set_display_x(s.mid)
                t.draw_annotate()
        else:
            x = self.text_anchor
            for y, s in zip(locs, labels):
                if not np.ma.is_masked(s):
                    t = AdjustableText(x=x, y=y, text=s, pointer=(0, y), **text_options)
                    texts.append(t)
                    segments.append(t.get_segment_y())
            lim = Segment(ax_bbox.ymin, ax_bbox.ymax)
            adjust_segments(lim, segments)
            for t, s in zip(texts, segments):
                t.set_display_y(s.mid)
                t.draw_annotate()

        ax.set_axis_off()
        if self.side != "top":
            ax.invert_yaxis()
        if self.side == "left":
            ax.invert_xaxis()


label_default_params = {
    "right": dict(align="left", rotation=0),
    "left": dict(align="right", rotation=0),
    "top": dict(align="bottom", rotation=90),
    "bottom": dict(align="top", rotation=90),
}


class Labels(_LabelBase):
    """Add text labels

    Parameters
    ----------
    labels : array of str
    align : str
        Which side of the text to align
    padding : float
        The buffer space between text and the adjcent plots, in points unit
    text_props : dict
        A dict of array that control the text properties for each text.
    label : str
        The label of the plot
    label_loc : {'top', 'bottom', 'left', 'right'}
        The location of the label
    label_props : dict
        The label properties
    options : dict
        Pass to :class:`matplotlib.text.Text`


    Examples
    --------

    To set the text properties for each text, use :code:`text_props`

    .. plot::
        :context: close-figs

        >>> labels = np.arange(20)
        >>> colors = ["r" if labels % 2 else "b" for labels in labels]

        >>> import marsilea as ma
        >>> from marsilea.plotter import Labels
        >>> h = ma.Heatmap(np.random.randn(20, 20))
        >>> h.add_right(Labels(labels, text_props={"color": colors}))
        >>> h.render()

    """

    def __init__(
        self,
        labels,
        align=None,
        padding=2,
        text_props=None,
        label=None,
        label_loc=None,
        label_props=None,
        **options,
    ):
        labels = self.data_validator(labels, target="1d")
        self.set_data(labels)
        self.texts = labels
        self.text_pad = 0
        self.text_gap = 0
        self.align = align
        self.padding = padding

        super().__init__()
        self._sort_params(**options)
        if text_props is not None:
            self.set_params(text_props)
        self.set_label(label, label_loc, label_props)

    def _align_compact(self, align):
        """Make align keyword compatible to any side"""
        if self.is_flank:
            checker = {"top": "right", "bottom": "left"}
        else:
            checker = {"right": "top", "left": "bottom"}
        return checker.get(align, align)

    def get_text_params(self) -> TextParams:
        default_params = label_default_params[self.side]
        if self.align is None:
            self.align = default_params["align"]

        self.align = self._align_compact(self.align)
        va, ha = self.align, "center"
        if self.is_flank:
            va, ha = ha, va

        p = TextParams(va=va, ha=ha, rotation=default_params["rotation"])
        p.update_params(self._user_params)

        return p

    def render_ax(self, spec):
        data = spec.data
        ax = spec.ax
        text_props = spec.params
        if text_props is None:
            text_props = [{}] * len(data)

        coords = self.get_axes_coords(data)
        params = self.get_text_params()
        if self.texts_size is not None:
            padding_px = self.padding / 72
            offset_ratio = padding_px / (self.texts_size + padding_px)
        else:
            offset_ratio = 0

        if self.is_flank:
            coords = coords[::-1]
        if self.align == "center":
            const = 0.5
        elif self.align in ["right", "top"]:
            const = 1 - offset_ratio / 2
        else:
            const = offset_ratio / 2  # self.text_pad / (1 + self.text_pad) / 2

        for s, c, p in zip(data, coords, text_props):
            x, y = (const, c) if self.is_flank else (c, const)
            options = {**params.to_dict(), **p}
            ax.text(x, y, s=s, transform=ax.transAxes, **options)
        ax.set_axis_off()
        # from matplotlib.patches import Rectangle
        # ax.add_artist(Rectangle((0, 0), 1, 1, edgecolor="r",
        #                         transform=ax.transAxes))


stick_pos = {
    "right": 0,
    "left": 1,
    "top": 0,
    "bottom": 1,
}


class Title(_LabelBase):
    """Add a title

    Parameters
    ----------
    title : str
        The title text
    align : {'center', 'left', 'right', 'bottom', 'top'}
        Where the title is placed
    padding : float
        The buffer space between text and the adjcent plots, in points unit
    fontsize : int, default: 12
        The title font size
    rotation :
    options : dict
        Pass to :class:`matplotlib.text.Text`

    See Also
    --------
        :meth:`marsilea.base.WhiteBoard.add_title`

    Examples
    --------

    .. plot::
        :context: close-figs

        >>> import marsilea as ma
        >>> from marsilea.plotter import Title
        >>> matrix = np.random.randn(15, 10)
        >>> h = ma.Heatmap(matrix)
        >>> for align in ["left", "right", "center"]:
        ...     title = Title(f"Title align={align}", align=align)
        ...     h.add_top(title)
        >>> for align in ["top", "bottom", "center"]:
        ...     title = Title(f"Title align={align}", align=align)
        ...     h.add_left(title)
        >>> h.render()


    """

    allow_split = False

    def __init__(
        self,
        title,
        align="center",
        padding=10,
        fontsize=None,
        fill_color=None,
        bordercolor=None,
        borderwidth=None,
        borderstyle=None,
        **options,
    ):
        self.title = title
        self.texts = [title]
        self.align = align
        if fontsize is None:
            fontsize = 12
        self.fontsize = fontsize
        self.text_pad = 0
        self.text_gap = 0
        self.rotation = 0
        self.padding = padding
        self.fill_color = fill_color
        self.bordercolor = bordercolor
        self.borderwidth = borderwidth
        self.borderstyle = borderstyle
        self._draw_bg = (self.fill_color is not None) or (self.bordercolor is not None)

        super().__init__()
        self._sort_params(**options)

    align_pos = {"right": 1, "left": 0, "top": 1, "bottom": 0, "center": 0.5}

    default_rotation = {
        "right": -90,
        "left": 90,
        "top": 0,
        "bottom": 0,
    }

    def _align_compact(self, align):
        """Make align keyword compatible to any side"""
        if self.is_flank:
            checker = {"left": "top", "right": "bottom"}
        else:
            checker = {"top": "left", "bottom": "right"}
        return checker.get(align, align)

    def get_text_params(self) -> TextParams:
        self.align = self._align_compact(self.align)
        va, ha = "center", self.align
        if self.is_flank:
            va, ha = ha, va

        p = TextParams(rotation=self.default_rotation[self.side], va=va, ha=ha)
        p.update_params(self._user_params)
        return p

    def render(self, ax):
        params = self.get_text_params()
        fontdict = params.to_dict()

        if self._draw_bg:
            bgcolor = "white" if self.fill_color is None else self.fill_color
            ax.add_artist(
                Rectangle(
                    (0, 0),
                    1,
                    1,
                    facecolor=self.fill_color,
                    edgecolor=self.bordercolor,
                    linewidth=self.borderwidth,
                    linestyle=self.borderstyle,
                    transform=ax.transAxes,
                )
            )

            fontdict.setdefault("color", self.get_text_color(bgcolor))

        const = self.align_pos[self.align]

        pos = 0.5
        x, y = (const, pos) if self.is_body else (pos, const)
        ax.text(
            x, y, self.title, fontsize=self.fontsize, transform=ax.transAxes, **fontdict
        )
        ax.set_axis_off()


class _ChunkBase(_LabelBase):
    def __init__(
        self,
        texts,
        fill_colors=None,
        align=None,
        props=None,
        padding=2,
        underline=False,
        bordercolor=None,
        borderwidth=None,
        borderstyle=None,
        **options,
    ):
        n = len(texts)
        self.n = n
        self.texts = texts
        self.align = align
        self.padding = padding

        if is_color_like(fill_colors):
            fill_colors = [fill_colors for _ in range(n)]
        if fill_colors is not None:
            fill_colors = np.asarray(fill_colors)
        self.fill_colors = fill_colors

        if props is None:
            props = [{} for _ in range(n)]
        elif isinstance(props, dict):
            props = [props for _ in range(n)]
        self.props = props

        self.underline = underline
        if is_color_like(bordercolor):
            bordercolor = [bordercolor for _ in range(n)]
        if bordercolor is not None:
            bordercolor = np.asarray(bordercolor)
        self.bordercolor = bordercolor

        if isinstance(borderwidth, Number):
            borderwidth = [borderwidth for _ in range(n)]
        self.borderwidth = borderwidth

        if isinstance(borderstyle, str):
            borderstyle = [borderstyle for _ in range(n)]
        self.borderstyle = borderstyle

        if self.underline:
            if self.bordercolor is None:
                self.bordercolor = np.asarray(["black" for _ in range(n)])
            if self.borderwidth is None:
                self.borderwidth = np.asarray([3 for _ in range(n)])

        self._draw_bg = (self.fill_colors is not None) or (self.bordercolor is not None)
        self.text_pad = 0

        super().__init__()
        self._sort_params(**options)

    align_pos = {"right": 1, "left": 0, "top": 1, "bottom": 0, "center": 0.5}

    default_align = {"right": "left", "left": "right", "top": "bottom", "bottom": "top"}

    default_rotation = {
        "right": -90,
        "left": 90,
        "top": 0,
        "bottom": 0,
    }

    default_underline = {
        "right": [(0, 0), (0, 1)],
        "left": [(1, 1), (1, 0)],
        "top": [(0, 1), (0, 0)],
        "bottom": [(0, 1), (1, 1)],
    }

    def get_alignment(self, ha, va, rotation):
        if rotation in {90, -90}:
            ha, va = va, ha  # swap the alignment
        align_x, align_y = self.align_pos[ha], self.align_pos[va]
        return align_x, align_y

    def _align_compact(self, align):
        """Make align keyword compatible to any side"""
        if self.is_flank:
            checker = {"top": "right", "bottom": "left"}
        else:
            checker = {"right": "top", "left": "bottom"}
        return checker.get(align, align)

    def get_text_params(self) -> TextParams:
        if self.align is None:
            self.align = self.default_align[self.side]

        self.align = self._align_compact(self.align)
        va, ha = self.align, "center"
        if self.is_flank:
            va, ha = ha, va

        rotation = self.default_rotation[self.side]
        p = TextParams(rotation=rotation, va=va, ha=ha)
        p.update_params(self._user_params)
        return p

    def _render(
        self, axes, texts, fill_colors, border_colors, borderwidth, borderstyle, props
    ):
        params = self.get_text_params()
        if self.texts_size is not None:
            padding_px = self.padding / 72
            offset_ratio = padding_px / (self.texts_size + padding_px)
        else:
            offset_ratio = 0

        if self.align == "center":
            const = 0.5
        elif self.align in ["right", "top"]:
            const = 1 - offset_ratio / 2
        else:
            const = offset_ratio / 2  # self.text_pad / (1 + self.text_pad) / 2

        # adjust the text alignment based on the alignment position and rotation
        c = 0.5
        x, y = (const, c) if self.is_flank else (c, const)

        fill_colors = [] if fill_colors is None else fill_colors
        border_colors = [] if border_colors is None else border_colors
        borderwidth = [] if borderwidth is None else borderwidth
        borderstyle = [] if borderstyle is None else borderstyle
        props = [] if props is None else props

        specs = zip_longest(
            axes, texts, fill_colors, border_colors, borderwidth, borderstyle, props
        )
        for ax, t, bgcolor, bc, lw, ls, prop in specs:
            ax.set_axis_off()
            fontdict = params.to_dict()
            if self._draw_bg:
                if bgcolor is None:
                    bgcolor = "white"
                if not self.underline:
                    rect = Rectangle(
                        (0, 0),
                        1,
                        1,
                        facecolor=bgcolor,
                        edgecolor=bc,
                        linewidth=lw,
                        linestyle=ls,
                        transform=ax.transAxes,
                    )
                else:
                    xdata, ydata = self.default_underline[self.side]
                    rect = Line2D(
                        xdata,
                        ydata,
                        color=bc,
                        linewidth=lw,
                        linestyle=ls,
                        transform=ax.transAxes,
                    )
                ax.add_artist(rect)
                fontdict.setdefault("color", self.get_text_color(bgcolor))

            if prop is not None:
                fontdict.update(prop)

            ax.text(x, y, t, fontdict=fontdict, transform=ax.transAxes)


class Chunk(_ChunkBase):
    """Mark groups

    This is useful to mark each groups after you split the plot,
    the order of the chunks will align with cluster order.

    Parameters
    ----------

    texts : array of str
        The label for each chunk
    fill_colors : color, array of color
        The color used as background color for each chunk
    borderwidth, bordercolor, borderstyle :
        Control the style of border, you can pass an array to style each group.
        For borderstyle, see :meth:`linestyles <matplotlib.lines.Line2D.set_linestyle>`
    props : dict or array of dict
        See :class:`matplotlib.text.Text`
    rotation : float
        How many angle to rotate the text coutner-clockwise, in degree unit
    padding : float
        The buffer space between text and the adjcent plots, in points unit
    label : str
        The label of the plot
    label_loc : {'right', 'left', 'top', 'bottom'}
        The location of the label
    label_props : dict
        The label properties

    See Also
    --------
        :class:`FixedChunk`

    Examples
    --------

    The order of chunk will be aligned with the order of cluster.

    .. plot::
        :context: close-figs

        >>> import marsilea as ma
        >>> from marsilea.plotter import Chunk
        >>> matrix = np.random.randn(20, 20)
        >>> h = ma.Heatmap(matrix)
        >>> chunk = ["C1", "C2", "C3", "C4"]
        >>> labels = np.random.choice(chunk, size=20)
        >>> h.group_rows(labels, order=chunk)
        >>> h.add_right(Chunk(chunk, bordercolor="gray"), pad=0.1)
        >>> h.add_dendrogram("left")
        >>> h.render()

    """

    def __init__(
        self,
        texts,
        fill_colors=None,
        *,
        align=None,
        props=None,
        padding=8,
        underline=False,
        bordercolor=None,
        borderwidth=None,
        borderstyle=None,
        label=None,
        label_loc=None,
        label_props=None,
        **options,
    ):
        super().__init__(
            texts,
            fill_colors=fill_colors,
            align=align,
            props=props,
            padding=padding,
            underline=underline,
            bordercolor=bordercolor,
            borderwidth=borderwidth,
            borderstyle=borderstyle,
            **options,
        )
        self.set_label(label, label_loc, label_props)

    def render(self, axes):
        if isinstance(axes, Axes):
            axes = [axes]

        if len(axes) != self.n:
            raise ValueError(
                f"You have {len(axes)} axes " f"but you only provide {self.n} texts."
            )

        texts = self.reindex_by_chunk(self.texts)
        fill_colors = self.reindex_by_chunk(self.fill_colors)
        border_colors = self.reindex_by_chunk(self.bordercolor)
        borderwidth = self.reindex_by_chunk(self.borderwidth)
        borderstyle = self.reindex_by_chunk(self.borderstyle)
        props = self.reindex_by_chunk(self.props)

        self._render(
            axes, texts, fill_colors, border_colors, borderwidth, borderstyle, props
        )

        if self._plan_label is not None:
            self._plan_label.add(axes, self.side)


class FixedChunk(_ChunkBase):
    """Mark groups with fixed order

    Parameters
    ----------
    texts : array of str
        The label for each chunk
    fill_colors : color, array of color
        The color used as background color for each chunk
    ratio : array of int
        To span chunks on more than one chunk.
    borderwidth, bordercolor, borderstyle :
        Control the style of border
        For borderstyle, see :meth:`linestyles <matplotlib.lines.Line2D.set_linestyle>`
    props : dict
        See :class:`matplotlib.text.Text`
    rotation : float
        How many to rotate the text
    padding : float
        The buffer space between text and the adjcent plots, in points unit
    label : str
        The label of the plot
    label_loc : {'right', 'left', 'top', 'bottom'}
        The location of the label
    label_props : dict
        The label properties


    See Also
    --------
        :class:`Chunk`

    Examples
    --------

    The fixed chunk will not be reordered by the cluster results.

    .. plot::
        :context: close-figs

        >>> import marsilea as ma
        >>> from marsilea.plotter import FixedChunk
        >>> matrix = np.random.randn(20, 20)
        >>> h = ma.Heatmap(matrix)
        >>> chunk = ["C1", "C2", "C3", "C4"]
        >>> labels = np.random.choice(chunk, size=20)
        >>> h.group_rows(labels, order=chunk)
        >>> h.add_right(FixedChunk(chunk, bordercolor="gray"), pad=0.1)
        >>> h.add_dendrogram("left")
        >>> h.render()

    You can span a chunk on more than one chunk.

    .. plot::
        :context: close-figs

        >>> h = ma.Heatmap(matrix)
        >>> chunk = ["C1", "C2-1", "C2-2", "C4"]
        >>> labels = np.random.choice(chunk, size=20)
        >>> h.group_rows(labels, order=chunk)
        >>> h.add_right(FixedChunk(chunk, bordercolor="gray"), pad=0.1)
        >>> h.add_right(
        ...     FixedChunk(
        ...         ["C1", "C2", "C3"],
        ...         fill_colors="red",
        ...         ratio=[1, 2, 1],
        ...     ),
        ...     pad=0.1,
        ... )
        >>> h.render()


    """

    def __init__(
        self,
        texts,
        fill_colors=None,
        *,
        align=None,
        ratio=None,
        props=None,
        padding=8,
        underline=False,
        bordercolor=None,
        borderwidth=None,
        borderstyle=None,
        label=None,
        label_loc=None,
        label_props=None,
        **options,
    ):
        super().__init__(
            texts,
            fill_colors,
            align=align,
            props=props,
            padding=padding,
            underline=underline,
            bordercolor=bordercolor,
            borderwidth=borderwidth,
            borderstyle=borderstyle,
            **options,
        )
        if ratio is not None:
            self.set_split_regroup(ratio)
        self.set_label(label, label_loc, label_props)

    def render(self, axes):
        if isinstance(axes, Axes):
            axes = [axes]

        if len(axes) != self.n:
            raise ValueError(
                f"You have {len(axes)} axes " f"but you only provide {self.n} texts."
            )

        self._render(
            axes,
            self.texts,
            self.fill_colors,
            self.bordercolor,
            self.borderwidth,
            self.borderstyle,
            self.props,
        )

        if self._plan_label is not None:
            self._plan_label.add(axes, self.side)
