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
        self._scroll_x = 0.0

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if self._text == value:
            return
        self._text = value
        self._cursor = max(0, min(self._cursor, len(value)))
        if self.focused:
            self._ensure_scroll()
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
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value: bool) -> None:
        if self._focused == value:
            return
        self._focused = value
        if not value:
            self._scroll_x = 0.0
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

    def _content_width(self) -> float:
        m = get_theme().metrics
        return max(0.0, self.paint_rect.width - 2 * m.input_padding_x)

    def _full_text_pixel_width(self, fm: QFontMetrics) -> float:
        before = self.text[: self.cursor]
        after = self.text[self.cursor :]
        return float(fm.horizontalAdvance(before + self.composition + after))

    def _caret_pixel_x(self, fm: QFontMetrics) -> float:
        return float(fm.horizontalAdvance(self._display_before_caret()))

    def _ensure_scroll(self, fm: QFontMetrics | None = None) -> None:
        """单行横向滚动：保证光标在内容区内，左侧被挤出的文字不绘制。"""
        if fm is None:
            fm = QFontMetrics(self._font())
        cw = self._content_width()
        if cw <= 0:
            self._scroll_x = 0.0
            return
        caret = self._caret_pixel_x(fm)
        full = self._full_text_pixel_width(fm)
        max_scroll = max(0.0, full - cw)
        sx = self._scroll_x
        if caret < sx:
            sx = caret
        elif caret > sx + cw:
            sx = caret - cw
        self._scroll_x = max(0.0, min(sx, max_scroll))

    def caret_qrect(self, visible: Rect) -> QRect:
        """光标矩形（Canvas 坐标），供 IME 定位候选窗。"""
        theme = get_theme()
        fm = QFontMetrics(self._font())
        if self.focused:
            self._ensure_scroll(fm)
        tx = self.paint_rect.x + theme.metrics.input_padding_x
        cx = tx + self._caret_pixel_x(fm) - self._scroll_x
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
        if self.focused:
            self._ensure_scroll()

    def move_cursor_to_x(self, screen_x: float) -> None:
        self.clear_composition()
        theme = get_theme()
        fm = QFontMetrics(self._font())
        r = self.paint_rect
        if self.focused:
            self._ensure_scroll(fm)
        local_x = max(
            0.0,
            screen_x - r.x - theme.metrics.input_padding_x + self._scroll_x,
        )
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
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    def backspace(self) -> None:
        if self._cursor <= 0:
            return
        pos = self._cursor
        self._text = self._text[: pos - 1] + self._text[pos:]
        self._cursor = pos - 1
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    def delete_forward(self) -> None:
        if self._cursor >= len(self._text):
            return
        pos = self._cursor
        self._text = self._text[:pos] + self._text[pos + 1 :]
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    def handle_input_method(self, event: QInputMethodEvent) -> bool:
        self.composition = event.preeditString()
        commit = event.commitString()
        if commit:
            self.insert(commit)
            self.composition = ""
        elif self.focused:
            self._ensure_scroll()
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
        content_w = self._content_width()
        if self.focused:
            self._ensure_scroll(fm)
        else:
            self._scroll_x = 0.0

        before = self.text[: self.cursor]
        after = self.text[self.cursor :]

        painter.save()
        painter.setClipRect(QRectF(tx, r.y, content_w, r.height))
        if before or self.composition or after:
            x = tx - self._scroll_x
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
        painter.restore()

        if self.focused and self._cursor_visible:
            cx = tx + self._caret_pixel_x(fm) - self._scroll_x
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


class TextArea(Node):
    """可编辑多行输入：超宽自动换行；Enter 硬换行；Ctrl+Enter 触发 on_submit。"""

    _LINE_GAP = 4.0

    def __init__(
        self,
        text: str = "",
        *,
        placeholder: str = "",
        min_lines: int = 3,
        min_width: float = 120,
        flex: float = 0,
        margin: float = 0,
        on_submit: Callable[[], None] | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(flex=flex, margin=margin, id=id)
        self._text = text
        self.placeholder = placeholder
        self.min_lines = max(1, min_lines)
        self.min_width = min_width
        self.on_submit = on_submit
        self._cursor = len(text)
        self._focused = False
        self._cursor_visible = True
        self.composition = ""
        self._scroll_y = 0.0
        self._scroll_x = 0.0

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if self._text == value:
            return
        self._text = value
        self._cursor = max(0, min(self._cursor, len(value)))
        if self.focused:
            self._ensure_scroll()
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
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value: bool) -> None:
        if self._focused == value:
            return
        self._focused = value
        if not value:
            self._scroll_y = 0.0
            self._scroll_x = 0.0
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

    def _line_height(self, fm: QFontMetrics) -> float:
        return float(fm.height()) + self._LINE_GAP

    def _logical_line_ranges(self) -> list[tuple[int, int]]:
        if not self._text:
            return [(0, 0)]
        ranges: list[tuple[int, int]] = []
        start = 0
        for i, ch in enumerate(self._text):
            if ch == "\n":
                ranges.append((start, i))
                start = i + 1
        ranges.append((start, len(self._text)))
        return ranges

    def _wrap_line_end(
        self, fm: QFontMetrics, start: int, para_end: int, max_w: float
    ) -> int:
        if start >= para_end:
            return para_end
        lo, hi = start + 1, para_end
        fit = start
        while lo <= hi:
            mid = (lo + hi) // 2
            if fm.horizontalAdvance(self._text[start:mid]) <= max_w:
                fit = mid
                lo = mid + 1
            else:
                hi = mid - 1
        if fit <= start:
            return min(start + 1, para_end)
        if fit < para_end:
            chunk = self._text[start:fit]
            sp = chunk.rfind(" ")
            if sp > 0:
                br = start + sp
                if fm.horizontalAdvance(self._text[start:br]) <= max_w:
                    return br
        return fit

    def _visual_line_ranges(self, fm: QFontMetrics | None = None) -> list[tuple[int, int]]:
        """绘制/命中用：先按 \\n 分段，再在内容宽度内软换行。"""
        if fm is None:
            fm = QFontMetrics(self._font())
        cw, _ = self._content_size(fm)
        if not self._text:
            return [(0, 0)]
        if cw <= 0:
            return self._logical_line_ranges()

        out: list[tuple[int, int]] = []
        for s, e in self._logical_line_ranges():
            if s >= e:
                out.append((s, e))
                continue
            if fm.horizontalAdvance(self._text[s:e]) <= cw:
                out.append((s, e))
                continue
            pos = s
            while pos < e:
                line_end = self._wrap_line_end(fm, pos, e, cw)
                out.append((pos, line_end))
                pos = line_end
                if pos < e and self._text[pos] == " ":
                    pos += 1
        return out if out else [(0, 0)]

    def _line_ranges(self) -> list[tuple[int, int]]:
        return self._visual_line_ranges()

    def _cursor_line_index(self, fm: QFontMetrics | None = None) -> int:
        c = self._cursor
        ranges = self._visual_line_ranges(fm)
        for i, (s, e) in enumerate(ranges):
            if s <= c < e:
                return i
            if c == e:
                if i + 1 < len(ranges) and ranges[i + 1][0] == e:
                    return i + 1
                return i
        return max(0, len(ranges) - 1)

    def _line_text(self, line_idx: int) -> str:
        ranges = self._line_ranges()
        if line_idx < 0 or line_idx >= len(ranges):
            return ""
        s, e = ranges[line_idx]
        return self._text[s:e]

    def _line_before_caret(self, fm: QFontMetrics | None = None) -> str:
        if fm is None:
            fm = QFontMetrics(self._font())
        li = self._cursor_line_index(fm)
        ranges = self._visual_line_ranges(fm)
        s, _ = ranges[li]
        return self._text[s : self._cursor] + self.composition

    def _content_size(self, fm: QFontMetrics) -> tuple[float, float]:
        m = get_theme().metrics
        r = self.paint_rect
        return (
            max(0.0, r.width - 2 * m.input_padding_x),
            max(0.0, r.height - 2 * m.input_padding_y),
        )

    def _caret_xy(self, fm: QFontMetrics) -> tuple[float, float]:
        lh = self._line_height(fm)
        li = self._cursor_line_index(fm)
        x = float(fm.horizontalAdvance(self._line_before_caret(fm)))
        y = li * lh
        return x, y

    def _content_height(self, fm: QFontMetrics) -> float:
        return len(self._line_ranges()) * self._line_height(fm)

    def _ensure_scroll(self, fm: QFontMetrics | None = None) -> None:
        if fm is None:
            fm = QFontMetrics(self._font())
        cw, ch = self._content_size(fm)
        if cw <= 0 or ch <= 0:
            self._scroll_y = 0.0
            self._scroll_x = 0.0
            return
        lh = self._line_height(fm)
        caret_x, caret_y = self._caret_xy(fm)
        full_h = self._content_height(fm)
        max_scroll_y = max(0.0, full_h - ch)
        sy = self._scroll_y
        if caret_y < sy:
            sy = caret_y
        elif caret_y + lh > sy + ch:
            sy = caret_y + lh - ch
        self._scroll_y = max(0.0, min(sy, max_scroll_y))

        # 软换行后通常无需横滚；IME 预编辑过长时仍横向跟随光标
        line_w = float(fm.horizontalAdvance(self._line_before_caret(fm)))
        max_scroll_x = max(0.0, line_w - cw)
        if max_scroll_x <= 0:
            self._scroll_x = 0.0
            return
        sx = self._scroll_x
        if caret_x < sx:
            sx = caret_x
        elif caret_x > sx + cw:
            sx = caret_x - cw
        self._scroll_x = max(0.0, min(sx, max_scroll_x))

    def scroll_by(self, delta_y: float) -> None:
        fm = QFontMetrics(self._font())
        _, ch = self._content_size(fm)
        full_h = self._content_height(fm)
        max_scroll_y = max(0.0, full_h - ch)
        self._scroll_y = max(0.0, min(self._scroll_y + delta_y, max_scroll_y))
        self.mark_paint_dirty()

    def caret_qrect(self, visible: Rect) -> QRect:
        theme = get_theme()
        fm = QFontMetrics(self._font())
        if self.focused:
            self._ensure_scroll(fm)
        m = theme.metrics
        r = self.paint_rect
        lh = self._line_height(fm)
        caret_x, caret_y = self._caret_xy(fm)
        cx = r.x + m.input_padding_x + caret_x - self._scroll_x
        cy = r.y + m.input_padding_y + caret_y - self._scroll_y + lh * 0.15
        return QRect(int(cx), int(cy), 1, max(1, int(lh * 0.7)))

    def measure(self, constraints: Constraints) -> Size:
        fm = QFontMetrics(self._font())
        lh = self._line_height(fm)
        m = get_theme().metrics
        min_h = 2 * m.input_padding_y + self.min_lines * lh
        if self.flex > 0:
            w = 0.0
        else:
            w = self.min_width
        return Size(min(w, constraints.max_width), min(min_h, constraints.max_height))

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        self._cursor = max(0, min(self._cursor, len(self._text)))
        if self.focused:
            self._ensure_scroll()

    def move_cursor_to_point(self, screen_x: float, screen_y: float) -> None:
        self.clear_composition()
        theme = get_theme()
        fm = QFontMetrics(self._font())
        m = theme.metrics
        r = self.paint_rect
        lh = self._line_height(fm)
        local_y = screen_y - r.y - m.input_padding_y + self._scroll_y
        line_idx = max(0, int(local_y / lh)) if lh > 0 else 0
        ranges = self._line_ranges()
        line_idx = min(line_idx, len(ranges) - 1)
        local_x = max(0.0, screen_x - r.x - m.input_padding_x)
        s, e = ranges[line_idx]
        line_text = self._text[s:e]
        col = 0
        for i in range(len(line_text) + 1):
            if fm.horizontalAdvance(line_text[:i]) > local_x:
                break
            col = i
        self.cursor = s + col

    def insert(self, ch: str) -> None:
        if not ch:
            return
        pos = self._cursor
        self._text = self._text[:pos] + ch + self._text[pos:]
        self._cursor = pos + len(ch)
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    def backspace(self) -> None:
        if self._cursor <= 0:
            return
        pos = self._cursor
        self._text = self._text[: pos - 1] + self._text[pos:]
        self._cursor = pos - 1
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    def delete_forward(self) -> None:
        if self._cursor >= len(self._text):
            return
        pos = self._cursor
        self._text = self._text[:pos] + self._text[pos + 1 :]
        if self.focused:
            self._ensure_scroll()
        self.mark_paint_dirty()

    def _move_vertical(self, delta: int) -> None:
        li = self._cursor_line_index()
        target = li + delta
        ranges = self._line_ranges()
        if target < 0 or target >= len(ranges):
            return
        s_cur, _ = ranges[li]
        s_tgt, e_tgt = ranges[target]
        col = self._cursor - s_cur
        self.cursor = s_tgt + min(col, e_tgt - s_tgt)

    def handle_input_method(self, event: QInputMethodEvent) -> bool:
        self.composition = event.preeditString()
        commit = event.commitString()
        if commit:
            self.insert(commit)
            self.composition = ""
        elif self.focused:
            self._ensure_scroll()
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

            self.insert(QApplication.clipboard().text().replace("\r\n", "\n").replace("\r", "\n"))
            return True

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                if self.on_submit is not None:
                    self.on_submit()
                return True
            self.insert("\n")
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
        if key == Qt.Key.Key_Up:
            self._move_vertical(-1)
            return True
        if key == Qt.Key.Key_Down:
            self._move_vertical(1)
            return True
        if key == Qt.Key.Key_Home:
            fm = QFontMetrics(self._font())
            ranges = self._visual_line_ranges(fm)
            s, _ = ranges[self._cursor_line_index(fm)]
            self.cursor = s
            return True
        if key == Qt.Key.Key_End:
            fm = QFontMetrics(self._font())
            ranges = self._visual_line_ranges(fm)
            _, e = ranges[self._cursor_line_index(fm)]
            self.cursor = e
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
        lh = self._line_height(fm)
        tx = r.x + m.input_padding_x
        ty = r.y + m.input_padding_y
        cw, ch = self._content_size(fm)
        if self.focused:
            self._ensure_scroll(fm)
        else:
            self._scroll_y = 0.0
            self._scroll_x = 0.0

        painter.save()
        painter.setClipRect(QRectF(tx, ty, cw, ch))
        ranges = self._visual_line_ranges(fm)
        cursor_line = self._cursor_line_index(fm)

        if not self._text and not self.focused and self.placeholder:
            painter.setPen(QColor(c.text_muted))
            painter.drawText(QPointF(tx, ty + fm.ascent()), self.placeholder)
        else:
            for i, (s, e) in enumerate(ranges):
                y = ty + i * lh - self._scroll_y
                if y + lh < ty or y > ty + ch:
                    continue
                scroll_x = self._scroll_x if i == cursor_line else 0.0
                x = tx - scroll_x
                if i == cursor_line and self.focused:
                    before = self._text[s : self._cursor]
                    after = self._text[self._cursor : e]
                    painter.setPen(QColor(c.input_text))
                    if before:
                        painter.drawText(QPointF(x, y + fm.ascent()), before)
                        x += fm.horizontalAdvance(before)
                    if self.composition:
                        painter.drawText(QPointF(x, y + fm.ascent()), self.composition)
                        comp_w = fm.horizontalAdvance(self.composition)
                        painter.drawLine(
                            int(x),
                            int(y + fm.ascent() + 2),
                            int(x + comp_w),
                            int(y + fm.ascent() + 2),
                        )
                        x += comp_w
                    if after:
                        painter.drawText(QPointF(x, y + fm.ascent()), after)
                else:
                    line = self._text[s:e]
                    if line:
                        painter.setPen(QColor(c.input_text))
                        painter.drawText(QPointF(x, y + fm.ascent()), line)
        painter.restore()

        if self.focused and self._cursor_visible:
            caret_x, caret_y = self._caret_xy(fm)
            cx = tx + caret_x - self._scroll_x
            cy = ty + caret_y - self._scroll_y
            painter.setPen(QColor(c.input_caret))
            painter.drawLine(
                int(cx),
                int(cy + lh * 0.15),
                int(cx),
                int(cy + lh * 0.85),
            )

        canvas = self._find_canvas()
        if canvas is not None:
            sr = canvas._node_screen_rect(self)
            self._last_painted_screen = Rect(sr.x, sr.y, sr.width, sr.height)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        lines = self._text.count("\n") + 1 if self._text else 0
        return (
            f"{pad}TextArea({lines} lines) "
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
