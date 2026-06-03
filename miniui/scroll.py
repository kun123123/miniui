"""可滚动视口：裁剪 + scroll_y 偏移，内容高度可大于视口。"""

from __future__ import annotations

from PyQt6.QtGui import QColor, QPainter

from .constraints import Constraints
from .geometry import Rect, Size
from .builder import UiScope
from .node import Node
from .theme import get_theme


class ScrollView(UiScope, Node):
    def __init__(
        self,
        child: Node | None = None,
        *,
        flex: float = 0,
        margin: float = 0,
    ) -> None:
        super().__init__(flex=flex, margin=margin)
        self.child: Node | None = None
        self.scroll_y = 0.0
        self._content_height = 0.0
        if child is not None:
            self.set_child(child)

    def set_child(self, child: Node) -> None:
        self.child = child
        child.parent = self
        canvas = child._find_canvas()
        if canvas is not None:
            canvas._bind_node_tree(child)
        self.mark_layout_dirty()

    @property
    def children(self) -> list[Node]:
        return [self.child] if self.child is not None else []

    def _clamp_scroll(self) -> None:
        max_y = max(0.0, self._content_height - self.rect.height)
        self.scroll_y = max(0.0, min(self.scroll_y, max_y))

    def scroll_by(self, dy: float) -> None:
        if self.child is None:
            return
        self.scroll_y += dy
        self._clamp_scroll()
        self.mark_paint_dirty()

    def measure(self, constraints: Constraints) -> Size:
        inner_w = max(0.0, constraints.max_width)
        if self.child is None:
            return Size(min(constraints.max_width, inner_w), 0.0)
        child_c = Constraints.loose(inner_w, 1e9)
        child_size = self.child._measure_with_margin(child_c)
        self._content_height = child_size.height

        if self.flex > 0:
            viewport_h = 0.0
        else:
            viewport_h = min(constraints.max_height, self._content_height)
        return Size(
            min(constraints.max_width, child_size.width),
            viewport_h,
        )

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        self._clamp_scroll()
        if self.child is None:
            return
        self.child._layout_with_margin(
            Rect(rect.x, rect.y, rect.width, self._content_height)
        )

    def paint(self, painter: QPainter) -> None:
        r = self.rect
        bg = QColor(get_theme().colors.canvas_bg)
        painter.fillRect(int(r.x), int(r.y), int(r.width), int(r.height), bg)
        painter.save()
        painter.setClipRect(int(r.x), int(r.y), int(r.width), int(r.height))
        painter.translate(0, -self.scroll_y)
        if self.child is not None:
            self.child.paint(painter)
        painter.restore()

    def paint_region(
        self,
        painter: QPainter,
        region: Rect,
        *,
        stats: dict[str, int] | None = None,
    ) -> None:
        """ScrollView：方案一 — 擦除已在 canvas 完成，此处只 paint 全部子节点。"""
        vr = self.rect
        if not vr.intersects(region):
            return
        if not self.subtree_paint_dirty():
            return
        if vr.intersect(region) is None:
            return
        painter.save()
        painter.setClipRect(int(vr.x), int(vr.y), int(vr.width), int(vr.height))
        painter.translate(0, -self.scroll_y)
        self._paint_all_children(painter)
        painter.restore()
        if stats is not None:
            self._count_leaf_stats(stats)
        self._clear_subtree_paint_dirty()

    def hit_test(self, x: float, y: float) -> Node | None:
        if not self.rect.contains(x, y) or self.child is None:
            return None
        return self.child.hit_test(x, y + self.scroll_y)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        lines = [
            f"{pad}ScrollView(scroll_y={self.scroll_y:.0f}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f}) "
            f"content_h={self._content_height:.0f}"
        ]
        if self.child is not None:
            lines.append(self.child.dump(indent + 1))
        return "\n".join(lines)
