"""
UI 节点基类。

三遍 pass（和真实 UI 框架一致）：
  1. measure(constraints)  子 → 父汇报「我需要多大」
  2. layout(rect)          父 → 子分配最终矩形
  3. paint(painter)        按 rect 绘制

局部重绘（方案一）：
  - 擦除：paintEvent clip 整块填画布色；叶节点 damage 只用于调度重画
  - 绘制：任一子节点 dirty → 父容器调度全部直接子节点 paint，父容器自身不 fill
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .constraints import Constraints
from .geometry import Rect, Size

if TYPE_CHECKING:
    from PyQt6.QtGui import QPainter


def _is_layout_container(node: Node) -> bool:
    """Row / Column 是布局容器；ScrollView 只是视口，不算。"""
    return type(node).__name__ in ("Row", "Column")


def _layout_change_affects_flex_siblings(child: Node, parent: Node) -> bool:
    """子容器主轴尺寸变化时，是否需要父 Row/Column 重新分配 flex。"""
    siblings = getattr(parent, "children", ())
    if not siblings:
        return False
    if child.flex > 0:
        return True
    return any(s.flex > 0 for s in siblings)


class Node(ABC):
    def __init__(
        self,
        *,
        flex: float = 0,
        margin: float = 0,
        id: str | None = None,
    ) -> None:
        self.rect = Rect(0, 0, 0, 0)
        self.parent: Node | None = None
        self.flex = flex
        self.margin = margin
        self.ui_id: str | None = id
        self._id_map: dict[str, Node] | None = None
        from .registry import bind_ui_id

        bind_ui_id(self, id)
        self._layout_dirty = True
        self._paint_dirty = True
        self._damage_rect: Rect | None = None
        self._canvas = None  # UiCanvas，由画布在挂载树时注入
        self.paint_dx = 0.0
        self.paint_dy = 0.0
        from .builder import auto_mount

        auto_mount(self)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other if isinstance(other, Node) else NotImplemented

    def _find_canvas(self):
        node: Node | None = self
        while node is not None:
            canvas = node._canvas
            if canvas is not None:
                return canvas
            node = node.parent
        return None

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
        """尺寸/结构变化：冒泡到最近 Row/Column；若影响 flex 兄弟则继续向父布局容器上升。"""
        self._layout_dirty = True
        self._paint_dirty = True

        container: Node | None = None
        if _is_layout_container(self):
            container = self
        else:
            p = self.parent
            while p is not None:
                if _is_layout_container(p):
                    container = p
                    break
                p = p.parent

        if container is None:
            self._schedule_layout_pass()
            return

        container._layout_dirty = True
        current = container

        while True:
            parent = current.parent
            while parent is not None and not _is_layout_container(parent):
                parent = parent.parent
            if parent is None:
                break
            if not _layout_change_affects_flex_siblings(current, parent):
                break
            parent._layout_dirty = True
            for s in getattr(parent, "children", ()):
                if s is not current and s.flex > 0:
                    s._layout_dirty = True
            current = parent

        self._schedule_layout_pass()

    def _schedule_layout_pass(self) -> None:
        canvas = self._find_canvas()
        if canvas is not None:
            canvas._schedule_relayout()

    def mark_paint_dirty(self) -> None:
        """仅外观变化（如按下态），不触发布局；已挂载画布时自动排队重绘。"""
        self._paint_dirty = True
        canvas = self._find_canvas()
        if canvas is not None:
            canvas._schedule_update()

    def set_damage(self, rect: Rect) -> None:
        """标记需重绘，并记录要擦除的屏幕区域（layout 变化时为旧∪新）。"""
        self._damage_rect = rect
        self._paint_dirty = True

    def merge_damage(self, rect: Rect) -> None:
        if self._damage_rect is None:
            self._damage_rect = rect
        else:
            self._damage_rect = Rect.union(self._damage_rect, rect)
        self._paint_dirty = True

    def clear_paint_state(self) -> None:
        self._paint_dirty = False
        self._damage_rect = None

    def subtree_paint_dirty(self) -> bool:
        if self._paint_dirty:
            return True
        for child in getattr(self, "children", ()):
            if child.subtree_paint_dirty():
                return True
        return False

    def subtree_layout_dirty(self) -> bool:
        if self._layout_dirty:
            return True
        for child in getattr(self, "children", ()):
            if child.subtree_layout_dirty():
                return True
        return False

    def clear_layout_dirty(self) -> None:
        self._layout_dirty = False

    def _has_paint_offset(self) -> bool:
        return self.paint_dx != 0.0 or self.paint_dy != 0.0

    def erase_before_repaint(self, painter: QPainter, bg) -> None:
        """方案一：只擦本节点 damage 矩形（画布色）。"""
        from .theme import fill_canvas_rect

        if self._damage_rect is None:
            return
        fill_canvas_rect(painter, self._damage_rect)

    def _paint_all_children(self, painter: QPainter) -> None:
        """方案一：父不重画自身，只 paint 全部直接子节点（含动画 translate）。"""
        children = getattr(self, "children", ())
        if self._has_paint_offset():
            painter.save()
            painter.translate(self.paint_dx, self.paint_dy)
            for child in children:
                child.paint(painter)
            painter.restore()
            return
        for child in children:
            child.paint(painter)

    def _container_intersects_region(self, region: Rect) -> bool:
        hit = self.paint_rect
        if self._has_paint_offset():
            hit = Rect.union(self.rect, self.paint_rect)
        if hit.intersects(region):
            return True
        for child in getattr(self, "children", ()):
            if child.paint_rect.intersects(region):
                return True
            if child._damage_rect is not None and child._damage_rect.intersects(region):
                return True
        return False

    def _count_leaf_stats(self, stats: dict[str, int]) -> None:
        for n in self.iter_subtree():
            if not getattr(n, "children", None):
                stats["nodes"] += 1

    def _paint_container(self, painter: QPainter) -> None:
        """整窗/full paint 用：fill 容器背景 + 全部子节点。"""
        from .theme import fill_canvas_rect

        children = getattr(self, "children", ())
        if self._has_paint_offset():
            cover = Rect.union(self.rect, self.paint_rect)
            fill_canvas_rect(painter, cover)
            painter.save()
            painter.translate(self.paint_dx, self.paint_dy)
            for child in children:
                child.paint(painter)
            painter.restore()
            return
        fill_canvas_rect(painter, self.paint_rect)
        for child in children:
            child.paint(painter)

    def _clear_subtree_paint_dirty(self) -> None:
        for node in self.iter_subtree():
            node.clear_paint_state()

    def paint_region(
        self,
        painter: QPainter,
        region: Rect,
        *,
        stats: dict[str, int] | None = None,
    ) -> None:
        """局部重绘：方案一（仅直接父层调度全部子节点 paint）。"""
        children = getattr(self, "children", None)
        if children:
            if not self._container_intersects_region(region):
                return
            if not self.subtree_paint_dirty():
                return
            if self._paint_dirty or self._has_paint_offset():
                self._paint_all_children(painter)
                self._clear_subtree_paint_dirty()
                if stats is not None:
                    self._count_leaf_stats(stats)
                return
            if any(
                ch._paint_dirty and not getattr(ch, "children", None)
                for ch in children
            ):
                self._paint_all_children(painter)
                self._clear_subtree_paint_dirty()
                if stats is not None:
                    self._count_leaf_stats(stats)
                return
            for child in children:
                if child.subtree_paint_dirty():
                    child.paint_region(painter, region, stats=stats)
            return

        if not self._paint_dirty:
            return
        if not self.paint_rect.intersects(region):
            return
        self.paint(painter)
        self.clear_paint_state()
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
