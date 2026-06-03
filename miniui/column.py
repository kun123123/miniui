"""纵向布局：spacing 与 padding 在 layout pass 里算 y 坐标。"""

from __future__ import annotations

from PyQt6.QtGui import QPainter

from .constraints import Constraints
from .flex import apply_flex, content_main, measure_children
from .geometry import Rect, Size
from .builder import UiScope
from .node import Node
from .theme import fill_canvas_rect


class Column(UiScope, Node):
    def __init__(
        self,
        children: list[Node] | None = None,
        *,
        padding: float = 0,
        spacing: float = 0,
        align: str = "start",
        flex: float = 0,
        margin: float = 0,
    ) -> None:
        super().__init__(flex=flex, margin=margin)
        self.children = children or []
        self.padding = padding
        self.spacing = spacing
        self.align = align  # start | center | stretch
        for child in self.children:
            child.parent = self
        self._child_sizes: list[Size] = []

    def add_child(self, child: Node) -> None:
        child.parent = self
        self.children.append(child)
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

        sizes = list(self._child_sizes)
        if any(c.flex > 0 for c in self.children):
            sizes = apply_flex(
                self.children,
                sizes,
                axis="vertical",
                inner_main=inner_h,
                spacing=self.spacing,
            )

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
        fill_canvas_rect(painter, self.paint_rect)
        for child in self.children:
            child.paint(painter)

    def hit_test(self, x: float, y: float) -> Node | None:
        if not self.rect.contains(x, y):
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
