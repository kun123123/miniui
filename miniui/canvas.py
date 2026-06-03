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
    QWheelEvent,
)
from PyQt6.QtWidgets import QApplication, QWidget

from .animation import animate_float
from .constraints import Constraints
from .geometry import Rect
from .node import Node
from .scroll import ScrollView
from .row import Row
from .theme import Theme, pop_theme, push_theme
from .widgets import Button, TextInput


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
        self.root = root
        self._theme = theme or Theme.light()
        if background is not None:
            self._bg = QColor(background)
        else:
            self._bg = QColor(self._theme.colors.canvas_bg)
        self._sync_widget_background()
        self._pressed_button: Button | None = None
        self._focused_input: TextInput | None = None
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
        self.setMouseTracking(False)
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._blink_cursor)
        self._cursor_timer.start(530)

    @property
    def theme(self) -> Theme:
        return self._theme

    def set_theme(self, theme: Theme) -> None:
        """换肤：只 mark_paint_dirty + 重绘，不 relayout。"""
        self._theme = theme
        self._bg = QColor(theme.colors.canvas_bg)
        self._sync_widget_background()
        for node in self.root.iter_subtree():
            node.mark_paint_dirty()
        self.update()

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

    def _layout_screen_rect(self, node: Node, rect: Rect) -> Rect:
        """layout rect 转屏幕坐标（ScrollView 内减 scroll_y）。"""
        r = rect
        p = node.parent
        while p is not None:
            if isinstance(p, ScrollView):
                r = Rect(r.x, r.y - p.scroll_y, r.width, r.height)
            p = p.parent
        return r

    def relayout(self, *, force: bool = False) -> None:
        """仅当根节点 layout_dirty（或 force）时执行 measure + layout。"""
        if not force and not self.root._layout_dirty:
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
            if prev is None or self._rect_changed(prev, cur):
                if prev is not None:
                    old_s = self._layout_screen_rect(node, prev)
                    new_s = self._layout_screen_rect(node, cur)
                    node.set_damage(Rect.union(old_s, new_s))
                else:
                    node.set_damage(self._layout_screen_rect(node, cur))
            else:
                if node._paint_dirty:
                    node.set_damage(self._layout_screen_rect(node, cur))
                else:
                    node.clear_paint_state()
        self.relayout_count += 1

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.root.mark_layout_dirty()
        self.relayout()

    def paintEvent(self, event) -> None:
        self.paint_count += 1
        if self.root._layout_dirty:
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
        if self.root._layout_dirty:
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

    def _ensure_dirty_damage(self) -> None:
        """dirty 但未设 damage 的节点（如按钮按下）用当前 paint_rect 补全。"""
        for node in self.root.iter_subtree():
            if not node._paint_dirty or node._damage_rect is not None:
                continue
            # ScrollView 内子项由视口统一擦除，不参与 damage 并集
            if self._is_scroll_content(node):
                continue
            node._damage_rect = self._node_screen_rect(node)

    def _collect_dirty_damage(self) -> Rect | None:
        region: Rect | None = None
        dirty_scrolls: list[ScrollView] = []
        for node in self.root.iter_subtree():
            if isinstance(node, ScrollView) and node.subtree_paint_dirty():
                dirty_scrolls.append(node)
            if not node._paint_dirty or node._damage_rect is None:
                continue
            if isinstance(node, ScrollView) or self._is_scroll_content(node):
                continue
            region = (
                node._damage_rect
                if region is None
                else Rect.union(region, node._damage_rect)
            )
        for scroll in dirty_scrolls:
            sd = self._scroll_damage(scroll)
            region = sd if region is None else Rect.union(region, sd)
        return region

    def _flush_repaint(self, *, sync: bool = True) -> None:
        """收集所有 dirty 节点的 damage 并集 → 擦除 → paintEvent 里只画 dirty 节点。"""
        self._ensure_dirty_damage()
        region = self._collect_dirty_damage()
        if region is None:
            return
        pad = 3.0
        region = Rect(
            region.x - pad,
            region.y - pad,
            region.width + 2 * pad,
            region.height + 2 * pad,
        )
        qr = self._region_qrect(region)
        if sync:
            self.repaint(qr)
        else:
            self.update(qr)

    def _paint_partial(self, painter: QPainter, region: Rect) -> None:
        qr = self._region_qrect(region)
        painter.fillRect(qr, self._bg)
        stats: dict[str, int] = {"nodes": 0}
        self.root.paint_region(painter, region, stats=stats)
        self.nodes_painted_last = stats["nodes"]

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.relayout(force=True)

    def _blink_cursor(self) -> None:
        if self._focused_input is None:
            return
        self._cursor_visible = not self._cursor_visible
        self.repaint_node(self._focused_input)

    def _set_focus(self, inp: TextInput | None) -> None:
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
            self.repaint_node(old)
        if inp is not None:
            inp.focused = True
            self.setFocus()
            self.repaint_node(inp)
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
            self.repaint_node(self._focused_input)
            self._update_input_method()
            event.accept()
            return
        super().inputMethodEvent(event)

    def invalidate(self) -> None:
        """先按需 relayout，再请求整窗重绘。"""
        self.relayout()
        self.update()

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
        """
        请求重绘：layout 脏则 relayout（仅 rect 变化的节点 set_damage）；
        否则只给当前节点设 damage；paintEvent 收集 dirty 并集后擦+画。
        """
        if isinstance(node, TextInput) and node is self._focused_input:
            node._cursor_visible = self._cursor_visible
        if self.root._layout_dirty:
            self.relayout()
        else:
            scroll = self._enclosing_scroll(node)
            if scroll is not None and node is not scroll:
                scroll.set_damage(self._node_screen_rect(scroll))
                node.mark_paint_dirty()
            else:
                node.set_damage(self._node_screen_rect(node))
        self._flush_repaint(sync=sync)

    def _repaint_button(self, btn: Button) -> None:
        """按钮外观变化时重绘；多按钮 Row（非 ScrollView 内）整行重绘，避免局部擦除留白。"""
        if self._enclosing_scroll(btn) is not None:
            self.repaint_node(btn)
            return
        parent = btn.parent
        if isinstance(parent, Row) and len(parent.children) > 1:
            for ch in parent.children:
                ch.mark_paint_dirty()
            self.repaint_node(parent)
        else:
            self.repaint_node(btn)

    def _repaint_scroll(self, scroll: ScrollView, *, sync: bool = False) -> None:
        """滚动后只擦 ScrollView 视口并重画列表，避免误擦同级搜索栏/添加栏。"""
        scroll.set_damage(self._node_screen_rect(scroll))
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
        super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        x, y = event.position().x(), event.position().y()
        hit = self.root.hit_test(x, y)
        if isinstance(hit, TextInput):
            self._set_focus(hit)
            hit.move_cursor_to_x(x)
            self.repaint_node(hit)
        else:
            self._set_focus(None)
        if isinstance(hit, Button):
            hit._pressed = True
            self._pressed_button = hit
            self._repaint_button(hit)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        x, y = event.position().x(), event.position().y()
        btn = self._pressed_button
        self._pressed_button = None
        if btn is not None:
            btn._pressed = False
            hit = self.root.hit_test(x, y)
            if hit is btn and btn.on_click is not None:
                btn.on_click()
            self._repaint_button(btn)
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self._focused_input is None:
            super().keyPressEvent(event)
            return
        if self._focused_input.handle_key(
            event.key(), event.text(), event.modifiers()
        ):
            self._cursor_visible = True
            self.repaint_node(self._focused_input)
            self._update_input_method()
            event.accept()
            return
        super().keyPressEvent(event)
