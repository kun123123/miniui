"""纵向布局：spacing 与 padding 在 layout pass 里算 y 坐标。"""

from __future__ import annotations

from PyQt6.QtGui import QPainter

from .constraints import Constraints
from .geometry import Rect, Size
from .node import Node


class Column(Node):
    def __init__(
        self,
        children: list[Node] | None = None,
        *,
        padding: float = 0,
        spacing: float = 0,
        align: str = "start",
    ) -> None:
        super().__init__()
        self.children = children or []
        self.padding = padding
        self.spacing = spacing
        self.align = align  # start | center | stretch
        for child in self.children:
            child.parent = self
        self._child_sizes: list[Size] = []

    def measure(self, constraints: Constraints) -> Size:
        inner_w = max(0.0, constraints.max_width - 2 * self.padding)
        inner_h = max(0.0, constraints.max_height - 2 * self.padding)

        self._child_sizes = []
        max_w = 0.0
        total_h = 0.0
        for i, child in enumerate(self.children):
            child_c = Constraints.loose(inner_w, inner_h)
            size = child.measure(child_c)
            self._child_sizes.append(size)
            max_w = max(max_w, size.width)
            total_h += size.height
            if i < len(self.children) - 1:
                total_h += self.spacing

        return Size(
            min(constraints.max_width, max_w + 2 * self.padding),
            min(constraints.max_height, total_h + 2 * self.padding),
        )

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        inner_x = rect.x + self.padding
        inner_y = rect.y + self.padding
        inner_w = max(0.0, rect.width - 2 * self.padding)

        y = inner_y
        for child, size in zip(self.children, self._child_sizes):
            child_x = inner_x
            if self.align == "center":
                child_x = inner_x + (inner_w - size.width) / 2
            elif self.align == "stretch":
                child_w = inner_w
                child.layout(Rect(inner_x, y, child_w, size.height))
                y += size.height + self.spacing
                continue

            child.layout(Rect(child_x, y, size.width, size.height))
            y += size.height + self.spacing

    def paint(self, painter: QPainter) -> None:
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
