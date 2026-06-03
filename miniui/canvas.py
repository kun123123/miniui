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

    def relayout(self, *, force: bool = False) -> None:
        """仅当根节点 layout_dirty（或 force）时执行 measure + layout。"""
        if not force and not self.root._layout_dirty:
            return
        w, h = self.width(), self.height()
        constraints = Constraints.loose(float(w), float(h))
        self.root.measure(constraints)
        self.root.layout(Rect(0, 0, float(w), float(h)))
        for node in self.root.iter_subtree():
            node.clear_layout_dirty()
        self.relayout_count += 1

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.root.mark_layout_dirty()
        self.relayout()

    def paintEvent(self, event) -> None:
        self.paint_count += 1
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
            node._paint_dirty = False

    def _paint_partial(self, painter: QPainter, region: Rect) -> None:
        qr = self._region_qrect(region)
        painter.fillRect(qr, self._bg)
        for node in self.root.iter_subtree():
            if node.paint_rect.intersects(region):
                node.mark_paint_dirty()
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
        """
        动画改变 paint_dx / paint_dy，不触发 relayout。

        dx/dy 为 (start, end)。layout 的 rect 不变，只有绘制位置在动。
        """
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

    def _node_screen_rect(self, node: Node) -> Rect:
        """节点在画布上的可见位置（ScrollView 内要减去 scroll_y）。"""
        r = node.paint_rect
        p = node.parent
        while p is not None:
            if isinstance(p, ScrollView):
                r = Rect(r.x, r.y - p.scroll_y, r.width, r.height)
            p = p.parent
        return r

    def repaint_node(self, node: Node, *, sync: bool = True) -> None:
        """
        只重绘某节点区域，不跑 measure/layout（除非 layout_dirty）。

        若节点因改文案等触发了 layout_dirty，会先 relayout，并重绘
        新旧 rect 的并集，避免文字变长/变短后局部区域不够擦除。
        """
        if isinstance(node, TextInput) and node is self._focused_input:
            node._cursor_visible = self._cursor_visible
        node.mark_paint_dirty()

        old_r: Rect | None = None
        if self.root._layout_dirty:
            old_r = self._node_screen_rect(node)
            self.relayout()

        r = self._node_screen_rect(node)
        if old_r is not None:
            r = Rect.union(old_r, r)

        qr = self._region_qrect(r)
        if sync:
            self.repaint(qr)
        else:
            self.update(qr)

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
            # 重绘列表所在 Column（含标题、搜索栏与 spacing 缝隙），避免局部重绘留白条
            target = scroll.parent if scroll.parent is not None else scroll
            self.repaint_node(target)
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
            self.repaint_node(hit)
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
            self.repaint_node(btn)
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
