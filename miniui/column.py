"""纵向布局：spacing 与 padding 在 layout pass 里算 y 坐标。"""

from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter

from .constraints import Constraints
from .flex import content_main, measure_children
from .geometry import Rect, Size
from .builder import UiScope
from .node import Node


class Column(UiScope, Node):
    def __init__(
        self,
        *nodes: Node,
        padding: float = 0,
        spacing: float = 0,
        align: str = "start",
        flex: float = 0,
        margin: float = 0,
        id: str | None = None,
        children: list[Node] | None = None,
    ) -> None:
        super().__init__(flex=flex, margin=margin, id=id)
        self.children = list(children) if children is not None else list(nodes)
        self.padding = padding
        self.spacing = spacing
        self.align = align  # start | center | stretch
        for child in self.children:
            child.parent = self
        self._child_sizes: list[Size] = []

    def add_child(self, child: Node) -> None:
        child.parent = self
        self.children.append(child)
        canvas = child._find_canvas()
        if canvas is not None:
            canvas._bind_node_tree(child)
        self.mark_layout_dirty()

    def remove_child(self, child: Node) -> None:
        if child not in self.children:
            return
        self.children.remove(child)
        child.parent = None
        self.mark_layout_dirty()

    def measure(self, constraints: Constraints) -> Size:
        inner_w = max(0.0, constraints.max_width - 2 * self.padding)
        inner_h = max(0.0, constraints.max_height - 2 * self.padding)

        self._child_sizes = measure_children(
            self.children,
            axis="vertical",
            inner_cross=inner_w,
            inner_main=inner_h,
            spacing=self.spacing,
        )
        max_w = max((s.width for s in self._child_sizes), default=0.0)

        has_flex = any(c.flex > 0 for c in self.children)
        if has_flex:
            total_h = inner_h
        else:
            total_h = content_main(
                self.children, self._child_sizes, axis="vertical", spacing=self.spacing
            )

        return Size(
            min(constraints.max_width, max_w + 2 * self.padding),
            min(constraints.max_height, total_h + 2 * self.padding),
        )

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        inner_x = rect.x + self.padding
        inner_y = rect.y + self.padding
        inner_w = max(0.0, rect.width - 2 * self.padding)
        inner_h = max(0.0, rect.height - 2 * self.padding)

        sizes = self._child_sizes

        y = inner_y
        n = len(self.children)
        for i, (child, size) in enumerate(zip(self.children, sizes)):
            h = size.height
            if self.align == "stretch":
                child._layout_with_margin(Rect(inner_x, y, inner_w, h))
            else:
                child_x = inner_x
                if self.align == "center":
                    child_x = inner_x + (inner_w - size.width) / 2
                child._layout_with_margin(Rect(child_x, y, size.width, h))
            if i < n - 1:
                y += h + self.spacing

    def paint(self, painter: QPainter) -> None:
        self._paint_container(painter)

    def hit_test(self, x: float, y: float) -> Node | None:
        if not self.visible or not self.rect.contains(x, y):
            return None
        for child in reversed(self.children):
            hit = child.hit_test(x, y)
            if hit is not None:
                return hit
        return self

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        lines = [
            f"{pad}Column(padding={self.padding}, spacing={self.spacing}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        ]
        for child in self.children:
            lines.append(child.dump(indent + 1))
        return "\n".join(lines)


class Panel(Column):
    """带圆角底色的纵向容器，适合工具栏 / 卡片区域。"""

    def __init__(
        self,
        *nodes: Node,
        padding: float = 0,
        spacing: float = 0,
        align: str = "start",
        flex: float = 0,
        margin: float = 0,
        id: str | None = None,
        children: list[Node] | None = None,
        color: str | None = None,
        radius: int | None = None,
        overlay_anchor: str | None = None,
    ) -> None:
        super().__init__(
            *nodes,
            padding=padding,
            spacing=spacing,
            align=align,
            flex=flex,
            margin=margin,
            id=id,
            children=children,
        )
        self._panel_color = color
        self._panel_radius = radius
        self.overlay_anchor = overlay_anchor

    def _fill_panel(self, painter: QPainter) -> None:
        from .theme import get_theme

        theme = get_theme()
        r = self.paint_rect
        fill = QColor(
            self._panel_color if self._panel_color is not None else theme.colors.box_fill
        )
        radius = (
            self._panel_radius
            if self._panel_radius is not None
            else theme.metrics.radius
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        painter.drawRoundedRect(QRectF(r.x, r.y, r.width, r.height), radius, radius)

    def paint(self, painter: QPainter) -> None:
        if not self.visible:
            return
        self._fill_panel(painter)
        self._paint_all_children(painter)

    def paint_region(
        self,
        painter: QPainter,
        region: Rect,
        *,
        stats: dict[str, int] | None = None,
    ) -> None:
        """局部重绘时先铺 Panel 底色，避免 clip 擦除后露画布色。"""
        if not self.visible:
            self._clear_subtree_paint_dirty()
            return
        children = getattr(self, "children", ())
        if not children:
            return super().paint_region(painter, region, stats=stats)
        if not self._container_intersects_region(region):
            return
        if not self.subtree_paint_dirty():
            return
        if Rect.intersect(self.paint_rect, region) is not None:
            self._fill_panel(painter)
        if self._paint_dirty or self._has_paint_offset():
            self._paint_all_children(painter)
            self._clear_subtree_paint_dirty()
            if stats is not None:
                self._count_leaf_stats(stats)
            return
        if any(
            ch._paint_dirty and not getattr(ch, "children", None) for ch in children
        ):
            self._paint_all_children(painter)
            self._clear_subtree_paint_dirty()
            if stats is not None:
                self._count_leaf_stats(stats)
            return
        for child in children:
            if child.subtree_paint_dirty():
                child.paint_region(painter, region, stats=stats)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        rect = self.rect
        return (
            f"{pad}Panel(padding={self.padding}, spacing={self.spacing}) "
            f"rect=({rect.x:.0f},{rect.y:.0f},{rect.width:.0f}x{rect.height:.0f})"
        )
