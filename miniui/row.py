"""横向布局：spacing 在 layout pass 里算 x 坐标。"""

from __future__ import annotations

from PyQt6.QtGui import QPainter

from .constraints import Constraints
from .flex import content_main, measure_children
from .geometry import Rect, Size
from .builder import UiScope
from .node import Node


class Row(UiScope, Node):
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
            axis="horizontal",
            inner_cross=inner_h,
            inner_main=inner_w,
            spacing=self.spacing,
        )
        max_h = max((s.height for s in self._child_sizes), default=0.0)

        has_flex = any(c.flex > 0 for c in self.children)
        if has_flex:
            total_w = inner_w
        else:
            total_w = content_main(
                self.children, self._child_sizes, axis="horizontal", spacing=self.spacing
            )

        return Size(
            min(constraints.max_width, total_w + 2 * self.padding),
            min(constraints.max_height, max_h + 2 * self.padding),
        )

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        inner_x = rect.x + self.padding
        inner_y = rect.y + self.padding
        inner_w = max(0.0, rect.width - 2 * self.padding)
        inner_h = max(0.0, rect.height - 2 * self.padding)

        sizes = self._child_sizes

        x = inner_x
        n = len(self.children)
        for i, (child, size) in enumerate(zip(self.children, sizes)):
            w = size.width
            h = size.height
            if self.align == "stretch":
                h = inner_h
            max_w = max(0.0, inner_x + inner_w - x)
            if i == n - 1:
                w = min(w, max_w)
            else:
                w = min(w, max(0.0, max_w - self.spacing))

            child_y = inner_y
            if self.align == "center":
                child_y = inner_y + (inner_h - h) / 2

            child._layout_with_margin(Rect(x, child_y, w, h))
            if i < n - 1:
                x += w + self.spacing

    def paint(self, painter: QPainter) -> None:
        self._paint_container(painter)

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
            f"{pad}Row(padding={self.padding}, spacing={self.spacing}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        ]
        for child in self.children:
            lines.append(child.dump(indent + 1))
        return "\n".join(lines)
