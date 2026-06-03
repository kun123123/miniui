"""Demo 09 · ScrollView：内容高于视口时滚轮滚动。

运行（在 code/ui 目录下）：
    python demos/scroll.py

验收点：
  - 下方列表项总高度大于可视区域，超出部分被裁剪
  - 鼠标在滚动区内滚轮：列表上下移动，scroll_y 变化
  - 滚到顶/底时不再越界
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Column, ScrollView, Text, Theme, UiCanvas

ITEMS = 12
COLORS = ("#ffcdd2", "#f8bbd0", "#e1bee7", "#c5cae9", "#bbdefb", "#b2dfdb")


def main() -> None:
    app = QApplication(sys.argv)

    list_column = Column(
        spacing=8,
        align="stretch",
        children=[
            Box(height=48, color=COLORS[i % len(COLORS)], label=f"第 {i + 1} 项")
            for i in range(ITEMS)
        ],
    )

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=12,
            children=[
                Text("滚轮在下方区域滚动列表", font_size=13),
                ScrollView(flex=1, child=list_column),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 09 · scroll")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 280)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
