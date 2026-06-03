"""Demo 11 · animate_offset：paint_dx/dy 偏移动画，不改变 layout。

运行（在 code/ui 目录下）：
    python demos/animation.py

验收点：
  - 点击按钮：色块沿水平方向平滑滑出 / 滑回
  - layout 槽位不变（拖动窗口时色块仍占原行宽）
  - 仅改 paint_dx，不 relayout
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Text, Theme, UiCanvas

SLIDE = 100.0


def main() -> None:
    app = QApplication(sys.argv)

    box = Box(height=56, color="#90caf9", label="paint_dx")
    busy = [False]

    def toggle() -> None:
        if busy[0]:
            return
        busy[0] = True
        at_rest = abs(box.paint_dx) < 1
        dx = (0.0, SLIDE) if at_rest else (box.paint_dx, 0.0)

        def done() -> None:
            busy[0] = False

        canvas.animate_offset(box, dx=dx, duration=400, on_finished=done)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=12,
            align="stretch",
            children=[
                Text("点击按钮：色块滑动，布局槽位保持不动", font_size=13),
                box,
                Button("右移 / 复位", on_click=toggle),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 11 · animation")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(400, 200)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
