"""PyQt 画布：窗口 resize 触发 measure + layout，paintEvent 触发绘制。"""

from __future__ import annotations

from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from .constraints import Constraints
from .geometry import Rect
from .node import Node


class UiCanvas(QWidget):
    """
    把 Node 树挂到 QWidget 上。

    你写的 UI 代码只负责「建树」；真正渲染发生在 paintEvent 里。
    """

    def __init__(self, root: Node, *, background: str = "#fafafa") -> None:
        super().__init__()
        self.root = root
        self._bg = QColor(background)
        self.setMinimumSize(480, 360)

    def relayout(self) -> None:
        w, h = self.width(), self.height()
        constraints = Constraints.loose(float(w), float(h))
        self.root.measure(constraints)
        self.root.layout(Rect(0, 0, float(w), float(h)))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.relayout()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self._bg)
        self.root.paint(painter)
        painter.end()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.relayout()
