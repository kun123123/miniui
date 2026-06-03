"""Demo 03 · flex：主轴剩余空间按比例分配。

运行（在 code/ui 目录下）：
    python demos/flex.py

验收点：
  - 拖动窗口宽度：中间 flex=1 的色块变宽，左右固定宽度不变
  - 无按钮、无交互，只看布局
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Row, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Row(
            padding=20,
            spacing=8,
            align="stretch",
            children=[
                Box(width=56, height=48, color="#ffcdd2", label="56"),
                Box(flex=1, height=48, color="#bbdefb", label="flex=1"),
                Box(width=72, height=48, color="#c8e6c9", label="72"),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 03 · flex")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(480, 120)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
