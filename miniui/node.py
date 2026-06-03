"""
UI 节点基类。

三遍 pass（和真实 UI 框架一致）：
  1. measure(constraints)  子 → 父汇报「我需要多大」
  2. layout(rect)          父 → 子分配最终矩形
  3. paint(painter)        按 rect 绘制
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .constraints import Constraints
from .geometry import Rect, Size

if TYPE_CHECKING:
    from PyQt6.QtGui import QPainter


class Node(ABC):
    def __init__(self, *, flex: float = 0, margin: float = 0) -> None:
        self.rect = Rect(0, 0, 0, 0)
        self.parent: Node | None = None
        self.flex = flex
        self.margin = margin
        self._layout_dirty = True
        self._paint_dirty = True
        self.paint_dx = 0.0
        self.paint_dy = 0.0
        from .builder import auto_mount

        auto_mount(self)

    @property
    def paint_rect(self) -> Rect:
        """绘制用矩形 = layout rect + 动画偏移（不改变布局/命中）。"""
        r = self.rect
        return Rect(
            r.x + self.paint_dx,
            r.y + self.paint_dy,
            r.width,
            r.height,
        )

    def reset_paint_offset(self) -> None:
        self.paint_dx = 0.0
        self.paint_dy = 0.0
        self.mark_paint_dirty()

    def mark_layout_dirty(self) -> None:
        """尺寸/结构可能变化：向上冒泡，根需要重新 measure + layout。"""
        self._layout_dirty = True
        self._paint_dirty = True
        if self.parent is not None and not self.parent._layout_dirty:
            self.parent.mark_layout_dirty()

    def mark_paint_dirty(self) -> None:
        """仅外观变化（如按下态），不触发布局。"""
        self._paint_dirty = True

    def subtree_paint_dirty(self) -> bool:
        if self._paint_dirty:
            return True
        for child in getattr(self, "children", ()):
            if child.subtree_paint_dirty():
                return True
        return False

    def clear_layout_dirty(self) -> None:
        self._layout_dirty = False

    def paint_region(
        self,
        painter: QPainter,
        region: Rect,
        *,
        stats: dict[str, int] | None = None,
    ) -> None:
        """仅绘制与 region 相交且子树含 paint_dirty 的节点。"""
        if not self.paint_rect.intersects(region):
            return

        children = getattr(self, "children", None)
        if children:
            if not self.subtree_paint_dirty():
                return
            inter = self.paint_rect.intersect(region)
            if inter is not None:
                from .theme import fill_canvas_rect

                fill_canvas_rect(painter, inter)
            for child in children:
                child.paint_region(painter, region, stats=stats)
            if self._paint_dirty:
                self._paint_dirty = False
            return

        if not self._paint_dirty:
            return
        self.paint(painter)
        self._paint_dirty = False
        if stats is not None:
            stats["nodes"] += 1

    def iter_subtree(self) -> Iterator[Node]:
        yield self
        for child in getattr(self, "children", ()):
            yield from child.iter_subtree()

    def _measure_with_margin(self, constraints: Constraints) -> Size:
        m = self.margin
        inner = Constraints.loose(
            max(0.0, constraints.max_width - 2 * m),
            max(0.0, constraints.max_height - 2 * m),
        )
        size = self.measure(inner)
        return Size(size.width + 2 * m, size.height + 2 * m)

    def _layout_with_margin(self, rect: Rect) -> None:
        m = self.margin
        self.layout(
            Rect(
                rect.x + m,
                rect.y + m,
                max(0.0, rect.width - 2 * m),
                max(0.0, rect.height - 2 * m),
            )
        )

    @abstractmethod
    def measure(self, constraints: Constraints) -> Size:
        ...

    @abstractmethod
    def layout(self, rect: Rect) -> None:
        ...

    @abstractmethod
    def paint(self, painter: QPainter) -> None:
        ...

    def hit_test(self, x: float, y: float) -> Node | None:
        if not self.rect.contains(x, y):
            return None
        return self

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        lines = [
            f"{pad}{self.__class__.__name__} "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        ]
        return "\n".join(lines)
