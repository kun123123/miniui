"""Demo 06 · Box：圆角色块（color / radius / label）。

运行（在 code/ui 目录下）：
    python demos/box.py

验收点：
  - 三个色块：自定义颜色、圆角、标签文字
  - 第三个不传 color，使用主题默认 box_fill
  - 无交互，只展示 Box 绘制
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Column, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=12,
            children=[
                Box(
                    width=220,
                    height=52,
                    color="#ef9a9a",
                    radius=12,
                    label="color + radius=12",
                ),
                Box(
                    width=220,
                    height=52,
                    color="#90caf9",
                    label="color + label",
                ),
                Box(width=220, height=52, label="theme default"),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 06 · box")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(320, 240)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
