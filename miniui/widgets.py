"""叶子节点：文本、色块、按钮。"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QPointF, Qt, QRect, QRectF
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QInputMethodEvent, QPainter

from .constraints import Constraints
from .geometry import Rect, Size
from .node import Node
from .text_layout import OverflowMode, fit_text_to_width

_BOX_LABEL_PAD_X = 8.0
from .theme import get_theme


def _qrectf(r: Rect) -> QRectF:
    """layout/paint 矩形 → Qt 浮点矩形，避免 int 截断与 damage 区域不一致。"""
    return QRectF(r.x, r.y, r.width, r.height)


class Text(Node):
    def __init__(
        self,
        text: str,
        *,
        font_size: int = 14,
        bold: bool = False,
        flex: float = 0,
        margin: float = 0,
        overflow: OverflowMode = "visible",
        id: str | None = None,
    ) -> None:
        super().__init__(flex=flex, margin=margin, id=id)
        self._text = text
        self.font_size = font_size
        self.bold = bold
        self.overflow = overflow
        self._font_key: tuple[str, int, bool] | None = None
        self._cached_font: QFont | None = None
        self._cached_fm: QFontMetrics | None = None
        self._display_key: tuple[str, int, str] | None = None
        self._display_value: str = text

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if self._text == value:
            return
        self._text = value
        self._display_key = None
        self.mark_layout_dirty()

    def _font(self) -> QFont:
        theme = get_theme()
        key = (theme.fonts.family, self.font_size, self.bold)
        if self._font_key != key:
            font = QFont(theme.fonts.family, self.font_size)
            font.setBold(self.bold)
            self._font_key = key
            self._cached_font = font
            self._cached_fm = QFontMetrics(font)
        return self._cached_font

    def _fm(self) -> QFontMetrics:
        self._font()
        assert self._cached_fm is not None
        return self._cached_fm

    def _display_for_paint(self) -> str:
        w = int(self.rect.width)
        key = (self._text, w, self.overflow)
        if self._display_key == key:
            return self._display_value
        display = fit_text_to_width(self._fm(), self._text, float(w), self.overflow)
        self._display_key = key
        self._display_value = display
        return display

    def warm_display(self, *extra_texts: str) -> None:
        """启动时预热 ellipsis 度量，避免首次 toggle 在 paint 里算长串。"""
        w = self.rect.width
        if w <= 0:
            return
        fm = self._fm()
        fit_text_to_width(fm, self._text, w, self.overflow)
        for t in extra_texts:
            fit_text_to_width(fm, t, w, self.overflow)

    def measure(self, constraints: Constraints) -> Size:
        fm = self._fm()
        w = min(float(fm.horizontalAdvance(self._text)), constraints.max_width)
        h = float(fm.height())
        return Size(w, h)

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        self._display_key = None

    def set_text(self, text: str) -> None:
        self.text = text

    def paint(self, painter: QPainter) -> None:
        theme = get_theme()
        painter.setFont(self._font())
        painter.setPen(QColor(theme.colors.text_primary))
        fm = self._fm()
        r = self.paint_rect
        baseline = r.y + (r.height + fm.ascent() - fm.descent()) / 2
        display = self._display_for_paint()
        painter.drawText(QPointF(r.x, baseline), display)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        return (
            f"{pad}Text({self._text!r}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        )


class Box(Node):
    """带背景色的矩形，用于可视化布局区域。"""

    def __init__(
        self,
        *,
        width: float | None = None,
        height: float | None = None,
        color: str | None = None,
        radius: int | None = None,
        label: str = "",
        flex: float = 0,
        margin: float = 0,
        id: str | None = None,
    ) -> None:
        super().__init__(flex=flex, margin=margin, id=id)
        self.fixed_width = width
        self.fixed_height = height
        self._custom_color = color
        self._custom_radius = radius
        self.label = label

    @property
    def color(self) -> str | None:
        return self._custom_color

    @color.setter
    def color(self, value: str | None) -> None:
        if self._custom_color == value:
            return
        self._custom_color = value
        self.mark_paint_dirty()

    def measure(self, constraints: Constraints) -> Size:
        if self.flex > 0:
            w = 0.0
            h = 0.0
        elif self.fixed_width is not None:
            w = self.fixed_width
        else:
            w = constraints.max_width
        if self.flex <= 0:
            if self.fixed_height is not None:
                h = self.fixed_height
            else:
                h = 40.0
        return Size(min(w, constraints.max_width), min(h, constraints.max_height))

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def paint(self, painter: QPainter) -> None:
        theme = get_theme()
        fill = (
            QColor(self._custom_color)
            if self._custom_color is not None
            else QColor(theme.colors.box_fill)
        )
        radius = (
            self._custom_radius
            if self._custom_radius is not None
            else theme.metrics.radius
        )
        r = self.paint_rect
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill)
        painter.drawRoundedRect(_qrectf(r), radius, radius)
        if self.label:
            font = QFont(theme.fonts.family, theme.fonts.size_body)
            painter.setFont(font)
            painter.setPen(QColor(theme.colors.box_label))
            max_w = max(0.0, r.width - 2 * _BOX_LABEL_PAD_X)
            display = fit_text_to_width(
                QFontMetrics(font), self.label, max_w, "ellipsis"
            )
            painter.drawText(QPointF(r.x + _BOX_LABEL_PAD_X, r.y + 20), display)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        name = f"Box({self.label!r})" if self.label else "Box"
        return f"{pad}{name} rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"


class Button(Node):
    def __init__(
        self,
        label: str,
        *,
        min_width: float = 72,
        height: float = 32,
        on_click: Callable[[], None] | None = None,
        flex: float = 0,
        margin: float = 0,
        id: str | None = None,
    ) -> None:
        super().__init__(flex=flex, margin=margin, id=id)
        self._label = label
        self.min_width = min_width
        self.height = height
        self.on_click = on_click
        self._pressed = False

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if self._label == value:
            return
        theme = get_theme()
        fm = QFontMetrics(QFont(theme.fonts.family, theme.fonts.size_body))
        old_w = max(self.min_width, float(fm.horizontalAdvance(self._label) + 24))
        new_w = max(self.min_width, float(fm.horizontalAdvance(value) + 24))
        self._label = value
        if old_w == new_w:
            self.mark_paint_dirty()
        else:
            self.mark_layout_dirty()

    @property
    def pressed(self) -> bool:
        return self._pressed

    @pressed.setter
    def pressed(self, value: bool) -> None:
        if self._pressed == value:
            return
        self._pressed = value
        self.mark_paint_dirty()

    def measure(self, constraints: Constraints) -> Size:
        theme = get_theme()
        fm = QFontMetrics(QFont(theme.fonts.family, theme.fonts.size_body))
        w = max(self.min_width, float(fm.horizontalAdvance(self._label) + 24))
        return Size(min(w, constraints.max_width), self.height)

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def paint(self, painter: QPainter) -> None:
        theme = get_theme()
        c = theme.colors
        m = theme.metrics
        r = self.paint_rect
        if self._pressed:
            painter.setPen(QColor(c.button_border_pressed))
            painter.setBrush(QColor(c.button_bg_pressed))
        else:
            painter.setPen(QColor(c.button_border))
            painter.setBrush(QColor(c.button_bg))
        painter.drawRoundedRect(_qrectf(r), m.radius, m.radius)
        painter.setPen(QColor(c.button_fg))
        painter.setFont(QFont(theme.fonts.family, theme.fonts.size_body))
        painter.drawText(
            _qrectf(r),
            Qt.AlignmentFlag.AlignCenter,
            self._label,
        )

        canvas = self._find_canvas()
        if canvas is not None:
            sr = canvas._node_screen_rect(self)
            self._last_painted_screen = Rect(sr.x, sr.y, sr.width, sr.height)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        return (
            f"{pad}Button({self._label!r}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        )


class TextInput(Node):
    """可编辑单行输入：点击聚焦，键盘/IME 输入，Enter 提交。"""

    def __init__(
        self,
        text: str = "",
        *,
        placeholder: str = "",
        height: float = 32,
        min_width: float = 120,
        flex: float = 0,
        margin: float = 0,
        on_submit: Callable[[], None] | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(flex=flex, margin=margin, id=id)
        self._text = text
        self.placeholder = placeholder
        self.height = height
        self.min_width = min_width
        self.on_submit = on_submit
        self._cursor = len(text)
        self._focused = False
        self._cursor_visible = True
        self.composition = ""

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if self._text == value:
            return
        self._text = value
        self._cursor = max(0, min(self._cursor, len(value)))
        self.mark_paint_dirty()

    @property
    def cursor(self) -> int:
        return self._cursor

    @cursor.setter
    def cursor(self, value: int) -> None:
        idx = max(0, min(int(value), len(self._text)))
        if self._cursor == idx:
            return
        self._cursor = idx
        self.mark_paint_dirty()

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value: bool) -> None:
        if self._focused == value:
            return
        self._focused = value
        self.mark_paint_dirty()

    def clear_composition(self) -> None:
        if not self.composition:
            return
        self.composition = ""
        self.mark_paint_dirty()

    def input_font(self) -> QFont:
        return self._font()

    def _font(self) -> QFont:
        theme = get_theme()
        return QFont(theme.fonts.family, theme.fonts.size_body)

    def _display_before_caret(self) -> str:
        return self.text[: self.cursor] + self.composition

    def caret_qrect(self, visible: Rect) -> QRect:
        """光标矩形（Canvas 坐标），供 IME 定位候选窗。"""
        theme = get_theme()
        fm = QFontMetrics(self._font())
        tx = self.paint_rect.x + theme.metrics.input_padding_x
        cx = tx + fm.horizontalAdvance(self._display_before_caret())
        return QRect(int(cx), int(visible.y), 1, max(1, int(visible.height)))

    def measure(self, constraints: Constraints) -> Size:
        if self.flex > 0:
            w = 0.0
        else:
            fm = QFontMetrics(self._font())
            content = self.text or self.placeholder
            w = max(self.min_width, float(fm.horizontalAdvance(content) + 16))
        return Size(min(w, constraints.max_width), self.height)

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        self._cursor = max(0, min(self._cursor, len(self._text)))

    def move_cursor_to_x(self, screen_x: float) -> None:
        self.clear_composition()
        theme = get_theme()
        fm = QFontMetrics(self._font())
        r = self.paint_rect
        local_x = max(0.0, screen_x - r.x - theme.metrics.input_padding_x)
        idx = 0
        for i in range(len(self._text) + 1):
            if fm.horizontalAdvance(self._text[:i]) > local_x:
                break
            idx = i
        self.cursor = idx

    def insert(self, ch: str) -> None:
        if not ch:
            return
        pos = self._cursor
        self._text = self._text[:pos] + ch + self._text[pos:]
        self._cursor = pos + len(ch)
        self.mark_paint_dirty()

    def backspace(self) -> None:
        if self._cursor <= 0:
            return
        pos = self._cursor
        self._text = self._text[: pos - 1] + self._text[pos:]
        self._cursor = pos - 1
        self.mark_paint_dirty()

    def delete_forward(self) -> None:
        if self._cursor >= len(self._text):
            return
        pos = self._cursor
        self._text = self._text[:pos] + self._text[pos + 1 :]
        self.mark_paint_dirty()

    def handle_input_method(self, event: QInputMethodEvent) -> bool:
        self.composition = event.preeditString()
        commit = event.commitString()
        if commit:
            self.insert(commit)
            self.composition = ""
        self.mark_paint_dirty()
        return True

    def handle_key(
        self,
        key: int,
        text: str,
        modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
    ) -> bool:
        if self.composition:
            return False

        if modifiers & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_V:
            from PyQt6.QtWidgets import QApplication

            clip = (
                QApplication.clipboard()
                .text()
                .replace("\r\n", " ")
                .replace("\n", " ")
                .replace("\r", " ")
            )
            for ch in clip:
                if ch.isprintable():
                    self.insert(ch)
            return True

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.on_submit is not None:
                self.on_submit()
            return True
        if key == Qt.Key.Key_Backspace:
            self.backspace()
            return True
        if key == Qt.Key.Key_Delete:
            self.delete_forward()
            return True
        if key == Qt.Key.Key_Left:
            self.cursor = max(0, self.cursor - 1)
            return True
        if key == Qt.Key.Key_Right:
            self.cursor = min(len(self.text), self.cursor + 1)
            return True
        if key == Qt.Key.Key_Home:
            self.cursor = 0
            return True
        if key == Qt.Key.Key_End:
            self.cursor = len(self.text)
            return True
        if text and len(text) == 1 and text.isprintable():
            self.insert(text)
            return True
        return False

    def paint(self, painter: QPainter) -> None:
        theme = get_theme()
        c = theme.colors
        m = theme.metrics
        r = self.paint_rect
        painter.setPen(
            QColor(c.input_border_focused if self.focused else c.input_border)
        )
        painter.setBrush(QColor(c.input_bg))
        painter.drawRoundedRect(_qrectf(r), m.radius, m.radius)

        font = self._font()
        painter.setFont(font)
        fm = QFontMetrics(font)
        baseline = r.y + (r.height + fm.ascent() - fm.descent()) / 2
        tx = r.x + m.input_padding_x

        before = self.text[: self.cursor]
        after = self.text[self.cursor :]

        if before or self.composition or after:
            x = tx
            painter.setPen(QColor(c.input_text))
            if before:
                painter.drawText(QPointF(x, baseline), before)
                x += fm.horizontalAdvance(before)
            if self.composition:
                painter.drawText(QPointF(x, baseline), self.composition)
                comp_w = fm.horizontalAdvance(self.composition)
                painter.drawLine(
                    int(x),
                    int(baseline + 2),
                    int(x + comp_w),
                    int(baseline + 2),
                )
                x += comp_w
            if after:
                painter.drawText(QPointF(x, baseline), after)
        elif self.placeholder:
            painter.setPen(QColor(c.text_muted))
            painter.drawText(QPointF(tx, baseline), self.placeholder)

        if self.focused and self._cursor_visible:
            cx = tx + fm.horizontalAdvance(self._display_before_caret())
            painter.setPen(QColor(c.input_caret))
            painter.drawLine(
                int(cx), int(r.y + 6), int(cx), int(r.y + r.height - 6)
            )

        canvas = self._find_canvas()
        if canvas is not None:
            sr = canvas._node_screen_rect(self)
            self._last_painted_screen = Rect(sr.x, sr.y, sr.width, sr.height)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        return (
            f"{pad}TextInput({self.text!r}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        )


class Spacer(Node):
    """弹性空白：配合 flex 吃掉剩余主轴空间，不绘制任何内容。"""

    def __init__(self, *, flex: float = 1, margin: float = 0, id: str | None = None) -> None:
        super().__init__(flex=flex, margin=margin, id=id)

    def measure(self, constraints: Constraints) -> Size:
        return Size.zero()

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def paint(self, painter: QPainter) -> None:
        pass

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        return (
            f"{pad}Spacer(flex={self.flex}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        )
