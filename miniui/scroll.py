"""可滚动视口：裁剪 + scroll_y 偏移，内容高度可大于视口。"""

from __future__ import annotations

from PyQt6.QtGui import QPainter

from .constraints import Constraints
from .geometry import Rect, Size
from .node import Node


class ScrollView(Node):
    def __init__(
        self,
        child: Node,
        *,
        flex: float = 0,
        margin: float = 0,
    ) -> None:
        super().__init__(flex=flex, margin=margin)
        self.child = child
        child.parent = self
        self.scroll_y = 0.0
        self._content_height = 0.0

    @property
    def children(self) -> list[Node]:
        return [self.child]

    def _clamp_scroll(self) -> None:
        max_y = max(0.0, self._content_height - self.rect.height)
        self.scroll_y = max(0.0, min(self.scroll_y, max_y))

    def scroll_by(self, dy: float) -> None:
        self.scroll_y += dy
        self._clamp_scroll()
        self.mark_paint_dirty()

    def measure(self, constraints: Constraints) -> Size:
        inner_w = max(0.0, constraints.max_width)
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
        self.child._layout_with_margin(
            Rect(rect.x, rect.y, rect.width, self._content_height)
        )

    def paint(self, painter: QPainter) -> None:
        r = self.rect
        painter.save()
        painter.setClipRect(int(r.x), int(r.y), int(r.width), int(r.height))
        painter.translate(0, -self.scroll_y)
        self.child.paint(painter)
        painter.restore()

    def paint_region(
        self,
        painter: QPainter,
        region: Rect,
        *,
        stats: dict[str, int] | None = None,
    ) -> None:
        vr = self.rect
        if not vr.intersects(region):
            return
        if not self.subtree_paint_dirty():
            return
        inter = vr.intersect(region)
        if inter is None:
            return
        painter.save()
        painter.setClipRect(int(vr.x), int(vr.y), int(vr.width), int(vr.height))
        painter.translate(0, -self.scroll_y)
        content_region = Rect(
            inter.x, inter.y + self.scroll_y, inter.width, inter.height
        )
        self.child.paint_region(painter, content_region, stats=stats)
        painter.restore()
        if self._paint_dirty:
            self._paint_dirty = False

    def hit_test(self, x: float, y: float) -> Node | None:
        if not self.rect.contains(x, y):
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
        lines.append(self.child.dump(indent + 1))
        return "\n".join(lines)
