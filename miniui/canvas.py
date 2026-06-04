"""PyQt 画布：窗口 resize 触发 measure + layout，paintEvent 触发绘制。"""

from __future__ import annotations

import math
from collections.abc import Callable

from PyQt6.QtCore import QEasingCurve, Qt, QTimer, QRect
from PyQt6.QtGui import (
    QColor,
    QInputMethodEvent,
    QKeyEvent,
    QMouseEvent,
    QPainter,
    QRegion,
    QWheelEvent,
)
from PyQt6.QtWidgets import QApplication, QWidget

from .animation import animate_float
from .constraints import Constraints
from .geometry import Rect
from .node import Node
from .scroll import ScrollView
from .theme import Theme, pop_theme, push_theme
from .widgets import Button, TextArea, TextInput


class UiCanvas(QWidget):
    """
    把 Node 树挂到 QWidget 上。

    你写的 UI 代码只负责「建树」；真正渲染发生在 paintEvent 里。
    """

    def __init__(
        self,
        root: Node,
        *,
        theme: Theme | None = None,
        background: str | None = None,
    ) -> None:
        super().__init__()
        self._root = root
        self._needs_relayout = False
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._process_scheduled_updates)
        self._theme = theme or Theme.light()
        if background is not None:
            self._bg = QColor(background)
        else:
            self._bg = QColor(self._theme.colors.canvas_bg)
        self._sync_widget_background()
        self._pressed_button: Button | None = None
        self._last_event_node: Node | None = None
        self._focused_input: TextInput | TextArea | None = None
        self._cursor_visible = True
        self.relayout_count = 0
        self.paint_count = 0
        self.full_paint_count = 0
        self.partial_paint_count = 0
        self.nodes_painted_last = 0
        self._running_anims: list = []
        self.setMinimumSize(480, 360)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setMouseTracking(False)
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._blink_cursor)
        self._cursor_timer.start(530)
        self._bind_node_tree(root)

    @property
    def root(self) -> Node:
        return self._root

    @root.setter
    def root(self, node: Node) -> None:
        self._root = node
        self._bind_node_tree(node)

    def _bind_node_tree(self, node: Node) -> None:
        """把画布引用挂到子树，供 mark_*_dirty 自动调度重绘。"""
        node._canvas = self
        for child in getattr(node, "children", ()):
            self._bind_node_tree(child)
        if isinstance(node, ScrollView) and node.child is not None:
            self._bind_node_tree(node.child)

    def _schedule_update(self) -> None:
        if not self._update_timer.isActive():
            self._update_timer.start(0)

    def _schedule_relayout(self) -> None:
        self._needs_relayout = True
        self._schedule_update()

    def request_repaint(self, *, sync: bool = False) -> None:
        """提交当前 dirty/damage，触发局部重绘（Bindings 列表刷新等）。"""
        self._flush_repaint(sync=sync)

    def _repaint_full(self, *, sync: bool = False) -> None:
        """整窗重绘：取消待处理的局部调度，只请求一次 Qt update/repaint。"""
        self._needs_relayout = False
        if self._update_timer.isActive():
            self._update_timer.stop()
        if sync:
            self.repaint()
        else:
            self.update()

    def _scroll_content_layout_dirty(self, node: Node) -> bool:
        cur: Node | None = node
        while cur is not None:
            if cur._layout_dirty:
                return True
            if isinstance(cur, ScrollView):
                break
            cur = cur.parent
        return False

    def _resolve_dirty_damage(self) -> None:
        """
        统一为 dirty 且无 damage 的节点计算屏幕 damage。

        - Row/Column：跳过（方案一容器不重画自身）
        - ScrollView 内叶节点：damage 设在视口，不写叶节点
        - 其它叶节点：set_damage(屏幕 paint_rect)
        """
        seen_scrolls: set[int] = set()

        for node in self.root.iter_subtree():
            if not node._paint_dirty or node._damage_rect is not None:
                continue
            if self._is_branch_container(node):
                continue

            if isinstance(node, TextInput) and node is self._focused_input:
                node._cursor_visible = self._cursor_visible

            scroll = self._enclosing_scroll(node)
            if scroll is not None and node is not scroll:
                if self._scroll_content_layout_dirty(node):
                    sid = id(scroll)
                    if sid not in seen_scrolls:
                        scroll.set_damage(self._node_screen_rect(scroll))
                        seen_scrolls.add(sid)
                else:
                    node.set_damage(self._node_screen_rect(node))
                continue

            screen = self._node_screen_rect(node)
            if isinstance(node, (TextInput, Button)):
                node.set_damage(self._border_damage(node, screen))
            else:
                node.set_damage(screen)

    def _process_scheduled_updates(self) -> None:
        if self.root.subtree_layout_dirty() or self._needs_relayout:
            self.relayout()
            self._needs_relayout = False
        self._flush_repaint(sync=False)

    @property
    def theme(self) -> Theme:
        return self._theme

    def set_theme(self, theme: Theme) -> None:
        """换肤：更新 theme token，整窗重绘，不 relayout。"""
        self._theme = theme
        self._bg = QColor(theme.colors.canvas_bg)
        self._sync_widget_background()
        self._repaint_full()

    def _sync_widget_background(self) -> None:
        pal = self.palette()
        pal.setColor(self.backgroundRole(), self._bg)
        self.setPalette(pal)

    @staticmethod
    def _region_qrect(region: Rect) -> QRect:
        """脏区转 QRect，右/下取 ceil，避免局部重绘留 1px 缝。"""
        x = int(region.x)
        y = int(region.y)
        w = max(1, math.ceil(region.right) - x)
        h = max(1, math.ceil(region.bottom) - y)
        return QRect(x, y, w, h)

    @staticmethod
    def _rect_changed(a: Rect, b: Rect) -> bool:
        return a.x != b.x or a.y != b.y or a.width != b.width or a.height != b.height

    _BORDER_DAMAGE_PAD = 2.0  # 圆角描边 + AA 会超出 layout 矩形

    @classmethod
    def _inflate_damage(cls, r: Rect) -> Rect:
        p = cls._BORDER_DAMAGE_PAD
        return Rect(r.x - p, r.y - p, r.width + 2 * p, r.height + 2 * p)

    def _border_damage(self, node: Node, screen: Rect) -> Rect:
        """带描边的控件：damage 外扩，并与上次绘制位置取并集，避免旧边框残留。"""
        dmg = self._inflate_damage(screen)
        last = getattr(node, "_last_painted_screen", None)
        if last is not None:
            dmg = Rect.union(dmg, self._inflate_damage(last))
        return dmg

    def _layout_screen_rect(self, node: Node, rect: Rect) -> Rect:
        """layout rect 转屏幕坐标（ScrollView 内减 scroll_y）。"""
        r = rect
        p = node.parent
        while p is not None:
            if isinstance(p, ScrollView):
                r = Rect(r.x, r.y - p.scroll_y, r.width, r.height)
            p = p.parent
        return r

    def _is_branch_container(self, node: Node) -> bool:
        """Row/Column 等：方案一局部重绘只画子节点，容器本身不参与 damage。"""
        children = getattr(node, "children", None)
        if not children:
            return False
        return not isinstance(node, ScrollView)

    def relayout(self, *, force: bool = False) -> None:
        """子树任一 layout_dirty（或 force）时，从根整树 measure + layout。"""
        if not force and not self.root.subtree_layout_dirty():
            return
        old_layout: dict[int, Rect] = {}
        for node in self.root.iter_subtree():
            r = node.rect
            old_layout[id(node)] = Rect(r.x, r.y, r.width, r.height)

        w, h = self.width(), self.height()
        constraints = Constraints.loose(float(w), float(h))
        self.root.measure(constraints)
        self.root.layout(Rect(0, 0, float(w), float(h)))

        for node in self.root.iter_subtree():
            node.clear_layout_dirty()
            prev = old_layout.get(id(node))
            cur = node.rect
            if self._is_branch_container(node):
                if node._paint_dirty:
                    node.clear_paint_state()
                continue
            if self._is_scroll_content(node):
                scroll = self._enclosing_scroll(node)
                if scroll is not None:
                    scroll._paint_dirty = True
                if prev is None or self._rect_changed(prev, cur):
                    node._paint_dirty = True
                node._damage_rect = None
                if not node._paint_dirty:
                    node.clear_paint_state()
                continue
            if prev is None or self._rect_changed(prev, cur):
                new_s = self._layout_screen_rect(node, cur)
                if prev is not None:
                    old_s = self._layout_screen_rect(node, prev)
                    if isinstance(node, (TextInput, Button)):
                        node.set_damage(
                            Rect.union(
                                self._border_damage(node, old_s),
                                self._border_damage(node, new_s),
                            )
                        )
                    else:
                        node.set_damage(Rect.union(old_s, new_s))
                elif isinstance(node, (TextInput, Button)):
                    node.set_damage(self._border_damage(node, new_s))
                else:
                    node.set_damage(new_s)
            elif node._paint_dirty:
                screen = self._layout_screen_rect(node, cur)
                if isinstance(node, (TextInput, Button)):
                    node.set_damage(self._border_damage(node, screen))
                else:
                    node.set_damage(screen)
            else:
                node.clear_paint_state()
        self.relayout_count += 1

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.root.mark_layout_dirty()
        self.relayout()

    def paintEvent(self, event) -> None:
        self.paint_count += 1
        if self.root.subtree_layout_dirty():
            self.relayout()
        if self._focused_input is not None:
            self._focused_input._cursor_visible = self._cursor_visible

        qr = event.rect()
        dirty = Rect(
            float(qr.x()), float(qr.y()), float(qr.width()), float(qr.height())
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        token = push_theme(self._theme)
        try:
            if self._is_full_repaint(dirty):
                self.full_paint_count += 1
                self._paint_full(painter)
            else:
                self.partial_paint_count += 1
                self._paint_partial(painter, dirty)
        finally:
            pop_theme(token)

        painter.end()

    def _is_full_repaint(self, dirty: Rect) -> bool:
        if not self.root.subtree_paint_dirty():
            return True
        if self.root.subtree_layout_dirty():
            return True
        w, h = float(self.width()), float(self.height())
        if w <= 0 or h <= 0:
            return True
        if dirty.width >= w - 2 and dirty.height >= h - 2:
            return True
        return False

    def _paint_full(self, painter: QPainter) -> None:
        painter.fillRect(self.rect(), self._bg)
        self.root.paint(painter)
        self.nodes_painted_last = sum(
            1 for node in self.root.iter_subtree() if not getattr(node, "children", None)
        )
        for node in self.root.iter_subtree():
            node.clear_paint_state()

    def _enclosing_scroll(self, node: Node) -> ScrollView | None:
        p = node.parent
        while p is not None:
            if isinstance(p, ScrollView):
                return p
            p = p.parent
        return None

    def _is_scroll_content(self, node: Node) -> bool:
        scroll = self._enclosing_scroll(node)
        return scroll is not None and node is not scroll

    def _scroll_damage(self, scroll: ScrollView) -> Rect:
        if scroll._damage_rect is not None:
            return scroll._damage_rect
        return self._node_screen_rect(scroll)

    def _scroll_repaint_needed(self, scroll: ScrollView) -> bool:
        """仅当视口或内容确有 damage 时才重绘 ScrollView，避免陈旧 dirty 牵连工具栏。"""
        if not scroll.subtree_paint_dirty():
            return False
        if scroll._paint_dirty or scroll._damage_rect is not None:
            return True
        if scroll.child is None:
            return False
        for node in scroll.child.iter_subtree():
            if node._damage_rect is not None:
                return True
        return False

    def _clear_stale_scroll_dirty(self, scroll: ScrollView) -> None:
        """清除仅有 paint_dirty、无 damage 的陈旧标记（不会触发有效重绘）。"""
        for node in scroll.iter_subtree():
            node.clear_paint_state()

    def _collect_dirty_damage_regions(self) -> list[Rect]:
        regions: list[Rect] = []
        seen_scrolls: set[int] = set()

        for node in self.root.iter_subtree():
            if isinstance(node, ScrollView):
                if id(node) in seen_scrolls:
                    continue
                seen_scrolls.add(id(node))
                if not self._scroll_repaint_needed(node):
                    self._clear_stale_scroll_dirty(node)
                    continue
                # 视口内任一 dirty → 脏区取整视口，与 paint_region 全画对齐
                regions.append(self._scroll_damage(node))
                continue
            if not node._paint_dirty or node._damage_rect is None:
                continue
            if self._is_branch_container(node):
                continue
            if self._is_scroll_content(node):
                continue
            regions.append(node._damage_rect)

        return regions

    def _flush_repaint(self, *, sync: bool = True) -> None:
        """
        局部重绘唯一出口：resolve damage → 收集 QRegion → Qt update/repaint。

        触发路径：
          1. mark_*_dirty → 定时器 → _process_scheduled_updates → 此处
          2. repaint_node / request_repaint / 动画 merge_damage → 此处
          3. 整窗 _repaint_full（换肤、invalidate）→ 不走此处
        """
        self._resolve_dirty_damage()
        regions = self._collect_dirty_damage_regions()
        if not regions:
            return
        qregion = QRegion()
        for sub in regions:
            qregion = qregion.united(self._region_qrect(sub))
        if sync:
            self.repaint(qregion)
        else:
            self.update(qregion)

    @staticmethod
    def _bounds_of_regions(regions: list[Rect]) -> Rect:
        bounds: Rect | None = None
        for r in regions:
            bounds = r if bounds is None else Rect.union(bounds, r)
        return bounds if bounds is not None else Rect(0, 0, 0, 0)

    def _paint_partial(self, painter: QPainter, region: Rect) -> None:
        """
        局部重绘：
          1. 先用画布色填满 paintEvent 的 clip（与 update(qregion) 对齐，避免扩区留缝）
          2. 再按 dirty 子树重画控件
        """
        from .theme import fill_canvas_rect

        fill_canvas_rect(painter, region)

        erase_regions = self._collect_dirty_damage_regions()
        paint_bounds = region
        if erase_regions:
            bounds = self._bounds_of_regions(erase_regions)
            clipped = Rect.intersect(bounds, region)
            if clipped is not None:
                paint_bounds = clipped

        stats: dict[str, int] = {"nodes": 0}
        self.root.paint_region(painter, paint_bounds, stats=stats)
        self.nodes_painted_last = stats["nodes"]

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.relayout(force=True)

    def _blink_cursor(self) -> None:
        if self._focused_input is None:
            return
        self._cursor_visible = not self._cursor_visible
        self.repaint_node(self._focused_input)

    def _set_focus(self, inp: TextInput | TextArea | None) -> None:
        if self._focused_input is inp:
            if inp is not None:
                self.setFocus()
            return
        old = self._focused_input
        self._focused_input = inp
        self._cursor_visible = True
        if old is not None:
            old.focused = False
            old.clear_composition()
        if inp is not None:
            inp.focused = True
            self.setFocus()
        self._update_input_method()

    def _update_input_method(self) -> None:
        QApplication.inputMethod().update(
            Qt.InputMethodQuery.ImCursorRectangle
            | Qt.InputMethodQuery.ImEnabled
        )

    def inputMethodQuery(self, query: Qt.InputMethodQuery):
        inp = self._focused_input
        if inp is None:
            return super().inputMethodQuery(query)
        if query == Qt.InputMethodQuery.ImEnabled:
            return True
        if query in (
            Qt.InputMethodQuery.ImCursorRectangle,
            Qt.InputMethodQuery.ImAnchorRectangle,
        ):
            return inp.caret_qrect(self._node_screen_rect(inp))
        if query == Qt.InputMethodQuery.ImFont:
            return inp.input_font()
        return super().inputMethodQuery(query)

    def inputMethodEvent(self, event: QInputMethodEvent) -> None:
        if self._focused_input is None:
            super().inputMethodEvent(event)
            return
        if self._focused_input.handle_input_method(event):
            self._cursor_visible = True
            self._update_input_method()
            event.accept()
            return
        super().inputMethodEvent(event)

    def invalidate(self) -> None:
        """先 relayout，再整窗重绘。"""
        self.relayout()
        self._repaint_full()

    def animate_offset(
        self,
        node: Node,
        *,
        dx: tuple[float, float] | None = None,
        dy: tuple[float, float] | None = None,
        duration: int = 350,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        """动画改变 paint_dx / paint_dy，不触发 relayout。"""
        count = int(dx is not None) + int(dy is not None)
        if count == 0:
            if on_finished is not None:
                on_finished()
            return

        remaining = [count]

        def wrap_done() -> None:
            remaining[0] -= 1
            if remaining[0] == 0 and on_finished is not None:
                on_finished()

        if dx is not None:
            animate_float(
                self,
                node,
                attr="paint_dx",
                start=dx[0],
                end=dx[1],
                duration=duration,
                easing=easing,
                on_finished=wrap_done,
            )
        if dy is not None:
            animate_float(
                self,
                node,
                attr="paint_dy",
                start=dy[0],
                end=dy[1],
                duration=duration,
                easing=easing,
                on_finished=wrap_done,
            )

    def _node_screen_rect(self, node: Node, *, use_layout_rect: bool = False) -> Rect:
        """节点在画布上的可见位置（ScrollView 内要减去 scroll_y）。"""
        r = node.rect if use_layout_rect else node.paint_rect
        p = node.parent
        while p is not None:
            if isinstance(p, ScrollView):
                r = Rect(r.x, r.y - p.scroll_y, r.width, r.height)
            p = p.parent
        return r

    def _node_layout_screen_rect(self, node: Node) -> Rect:
        """layout 槽位的屏幕区域（不含 paint_dx/dy），动画时需一并擦除。"""
        return self._node_screen_rect(node, use_layout_rect=True)

    def repaint_node(self, node: Node, *, sync: bool = True) -> None:
        """请求重绘指定节点（flush 前由 _resolve_dirty_damage 统一算 damage）。"""
        if self.root.subtree_layout_dirty():
            self.relayout()
        node._paint_dirty = True
        self._flush_repaint(sync=sync)

    def _repaint_scroll(self, scroll: ScrollView, *, sync: bool = False) -> None:
        """滚动后重绘 ScrollView 视口（scroll_by 已 mark_paint_dirty）。"""
        self._flush_repaint(sync=sync)

    def _scroll_at(self, x: float, y: float) -> ScrollView | None:
        return self._find_scroll(self.root, x, y)

    def _find_scroll(self, node: Node, x: float, y: float) -> ScrollView | None:
        if not node.rect.contains(x, y):
            return None
        if isinstance(node, ScrollView):
            return node
        for child in reversed(getattr(node, "children", ())):
            found = self._find_scroll(child, x, y)
            if found is not None:
                return found
        return None

    def wheelEvent(self, event: QWheelEvent) -> None:
        x, y = event.position().x(), event.position().y()
        scroll = self._scroll_at(x, y)
        if scroll is not None:
            delta = event.angleDelta().y()
            scroll.scroll_by(-delta / 120.0 * 28.0)
            self._repaint_scroll(scroll)
            event.accept()
            return
        hit = self.root.hit_test(x, y)
        if isinstance(hit, TextArea):
            hit.scroll_by(-event.angleDelta().y() / 120.0 * 28.0)
            self.repaint_node(hit)
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        x, y = event.position().x(), event.position().y()
        hit = self.root.hit_test(x, y)
        if isinstance(hit, TextInput):
            self._set_focus(hit)
            hit.move_cursor_to_x(x)
        elif isinstance(hit, TextArea):
            self._set_focus(hit)
            hit.move_cursor_to_point(x, y)
        elif not isinstance(hit, Button):
            self._set_focus(None)
        if isinstance(hit, Button):
            hit.pressed = True
            self._pressed_button = hit
            self._last_event_node = hit
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        x, y = event.position().x(), event.position().y()
        btn = self._pressed_button
        self._pressed_button = None
        if btn is not None:
            btn.pressed = False
            screen = self._node_screen_rect(btn)
            if screen.contains(x, y) and btn.on_click is not None:
                if self._focused_input is not None:
                    self._set_focus(None)
                fn = btn.on_click
                QTimer.singleShot(0, fn)
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self._focused_input is None:
            super().keyPressEvent(event)
            return
        if self._focused_input.handle_key(
            event.key(), event.text(), event.modifiers()
        ):
            self._cursor_visible = True
            self._update_input_method()
            event.accept()
            return
        super().keyPressEvent(event)
