"""层叠布局：底层铺满，overlay_anchor 子节点叠在上方（如底部控制条）。"""

from __future__ import annotations

from PyQt6.QtGui import QPainter

from .constraints import Constraints
from .geometry import Rect, Size
from .node import Node


class Stack(Node):
    def __init__(
        self,
        *nodes: Node,
        flex: float = 0,
        margin: float = 0,
        id: str | None = None,
        children: list[Node] | None = None,
    ) -> None:
        super().__init__(flex=flex, margin=margin, id=id)
        self.children = list(children) if children is not None else list(nodes)
        for child in self.children:
            child.parent = self
        self._child_sizes: list[Size] = []

    def measure(self, constraints: Constraints) -> Size:
        self._child_sizes = [
            child._measure_with_margin(constraints) for child in self.children
        ]
        if self.flex > 0:
            return Size(constraints.max_width, 0.0)
        return Size(constraints.max_width, constraints.max_height)

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        for child, size in zip(self.children, self._child_sizes):
            anchor = getattr(child, "overlay_anchor", None)
            if anchor == "bottom":
                h = size.height + 2 * child.margin
                child._layout_with_margin(
                    Rect(rect.x, rect.y + rect.height - h, rect.width, h)
                )
            else:
                child._layout_with_margin(rect)

    def _paint_visible_children(self, painter: QPainter) -> None:
        for child in self.children:
            if child.visible:
                child.paint(painter)

    def paint(self, painter: QPainter) -> None:
        self._paint_visible_children(painter)

    def paint_region(
        self,
        painter: QPainter,
        region: Rect,
        *,
        stats: dict[str, int] | None = None,
    ) -> None:
        if not self._container_intersects_region(region):
            return
        if not self.subtree_paint_dirty():
            return

        bases: list[Node] = []
        overlays: list[Node] = []
        for child in self.children:
            if getattr(child, "overlay_anchor", None):
                overlays.append(child)
            else:
                bases.append(child)

        base_painted = False
        for child in bases:
            if child.subtree_paint_dirty():
                child.paint_region(painter, region, stats=stats)
                base_painted = True

        for child in overlays:
            if not child.visible:
                continue
            if child.subtree_paint_dirty():
                child.paint_region(painter, region, stats=stats)
            elif base_painted and Rect.intersect(child.paint_rect, region) is not None:
                child.paint(painter)
                child._clear_subtree_paint_dirty()
                if stats is not None:
                    child._count_leaf_stats(stats)

    def hit_test(self, x: float, y: float) -> Node | None:
        if not self.rect.contains(x, y):
            return None
        for child in reversed(self.children):
            if not child.visible:
                continue
            hit = child.hit_test(x, y)
            if hit is not None:
                return hit
        return self

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        lines = [
            f"{pad}Stack rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        ]
        for child in self.children:
            lines.append(child.dump(indent + 1))
        return "\n".join(lines)
