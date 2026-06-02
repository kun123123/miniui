"""横向布局：spacing 在 layout pass 里算 x 坐标。"""

from __future__ import annotations

from PyQt6.QtGui import QPainter

from .constraints import Constraints
from .geometry import Rect, Size
from .node import Node


class Row(Node):
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
        max_h = 0.0
        total_w = 0.0
        for i, child in enumerate(self.children):
            child_c = Constraints.loose(inner_w, inner_h)
            size = child.measure(child_c)
            self._child_sizes.append(size)
            max_h = max(max_h, size.height)
            total_w += size.width
            if i < len(self.children) - 1:
                total_w += self.spacing

        return Size(
            min(constraints.max_width, total_w + 2 * self.padding),
            min(constraints.max_height, max_h + 2 * self.padding),
        )

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        inner_x = rect.x + self.padding
        inner_y = rect.y + self.padding
        inner_h = max(0.0, rect.height - 2 * self.padding)

        x = inner_x
        for child, size in zip(self.children, self._child_sizes):
            child_y = inner_y
            if self.align == "center":
                child_y = inner_y + (inner_h - size.height) / 2
            elif self.align == "stretch":
                child.layout(Rect(x, inner_y, size.width, inner_h))
                x += size.width + self.spacing
                continue

            child.layout(Rect(x, child_y, size.width, size.height))
            x += size.width + self.spacing

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
            f"{pad}Row(padding={self.padding}, spacing={self.spacing}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        ]
        for child in self.children:
            lines.append(child.dump(indent + 1))
        return "\n".join(lines)
