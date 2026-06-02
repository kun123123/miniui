"""叶子节点：文本、色块、按钮。"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter

from .constraints import Constraints
from .geometry import Rect, Size
from .node import Node


class Text(Node):
    def __init__(self, text: str, *, font_size: int = 14, bold: bool = False) -> None:
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.bold = bold

    def _font(self) -> QFont:
        font = QFont("Microsoft YaHei", self.font_size)
        font.setBold(self.bold)
        return font

    def measure(self, constraints: Constraints) -> Size:
        fm = QFontMetrics(self._font())
        w = min(float(fm.horizontalAdvance(self.text)), constraints.max_width)
        h = float(fm.height())
        return Size(w, h)

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def paint(self, painter: QPainter) -> None:
        painter.setFont(self._font())
        painter.setPen(QColor(30, 30, 30))
        fm = QFontMetrics(self._font())
        baseline = self.rect.y + fm.ascent() + 2
        painter.drawText(int(self.rect.x), int(baseline), self.text)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        return (
            f"{pad}Text({self.text!r}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        )


class Box(Node):
    """带背景色的矩形，用于可视化布局区域。"""

    def __init__(
        self,
        *,
        width: float | None = None,
        height: float | None = None,
        color: str = "#e8eef8",
        radius: int = 6,
        label: str = "",
    ) -> None:
        super().__init__()
        self.fixed_width = width
        self.fixed_height = height
        self.color = QColor(color)
        self.radius = radius
        self.label = label

    def measure(self, constraints: Constraints) -> Size:
        w = self.fixed_width if self.fixed_width is not None else constraints.max_width
        h = self.fixed_height if self.fixed_height is not None else 40.0
        return Size(min(w, constraints.max_width), min(h, constraints.max_height))

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def paint(self, painter: QPainter) -> None:
        r = self.rect
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        painter.drawRoundedRect(
            int(r.x), int(r.y), int(r.width), int(r.height), self.radius, self.radius
        )
        if self.label:
            painter.setPen(QColor(60, 60, 80))
            painter.drawText(int(r.x + 8), int(r.y + 20), self.label)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        name = f"Box({self.label!r})" if self.label else "Box"
        return f"{pad}{name} rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"


class Button(Node):
    def __init__(self, label: str, *, min_width: float = 72, height: float = 32) -> None:
        super().__init__()
        self.label = label
        self.min_width = min_width
        self.height = height

    def measure(self, constraints: Constraints) -> Size:
        fm = QFontMetrics(QFont("Microsoft YaHei", 13))
        w = max(self.min_width, float(fm.horizontalAdvance(self.label) + 24))
        return Size(min(w, constraints.max_width), self.height)

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def paint(self, painter: QPainter) -> None:
        r = self.rect
        painter.setPen(QColor(100, 120, 200))
        painter.setBrush(QColor(235, 240, 255))
        painter.drawRoundedRect(int(r.x), int(r.y), int(r.width), int(r.height), 6, 6)
        painter.setPen(QColor(40, 50, 90))
        painter.setFont(QFont("Microsoft YaHei", 13))
        fm = QFontMetrics(painter.font())
        tx = r.x + (r.width - fm.horizontalAdvance(self.label)) / 2
        ty = r.y + (r.height + fm.ascent() - fm.descent()) / 2
        painter.drawText(int(tx), int(ty), self.label)

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        return (
            f"{pad}Button({self.label!r}) "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        )
