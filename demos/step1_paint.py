"""
Step 1：没有框架，直接在 paintEvent 里画矩形。

目的：建立直觉——屏幕上的一切 = QPainter + (x, y, w, h)。
运行：python demos/step1_paint.py
"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QApplication, QWidget


class Step1Widget(QWidget):
    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#fafafa"))

        # 三个区域的位置是「写死的」——还没有 layout 引擎
        rects = [
            (24, 24, 432, 48, "#dce8ff", "标题区"),
            (24, 88, 432, 120, "#e8f5e9", "内容区"),
            (24, 224, 200, 36, "#fff3e0", "按钮 A"),
        ]
        for x, y, w, h, color, label in rects:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(color))
            p.drawRoundedRect(x, y, w, h, 6, 6)
            p.setPen(QColor(40, 40, 40))
            p.setFont(QFont("Microsoft YaHei", 12))
            p.drawText(x + 10, y + 24, label)

        p.setPen(QColor(200, 60, 60))
        p.setFont(QFont("Microsoft YaHei", 10))
        p.drawText(24, 280, "↑ 间距、位置全是手写数字，改布局要改多处坐标")


def main() -> None:
    app = QApplication(sys.argv)
    w = Step1Widget()
    w.resize(480, 320)
    w.setWindowTitle("Step 1 · 手写坐标绘制")
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
