"""Demo 05 · Spacer：吃掉 Row 主轴剩余空间。

运行（在 code/ui 目录下）：
    python demos/spacer.py

验收点：
  - 左右两个色块宽度固定，始终贴在 Row 两侧（中间 Spacer 撑开）
  - 拖动窗口变宽：只有中间空白变宽，色块宽度不变
  - Spacer 本身不可见、不绘制
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Row, Spacer, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Row(
            padding=20,
            align="center",
            children=[
                Box(width=80, height=44, color="#ffab91", label="左"),
                Spacer(flex=1),
                Box(width=80, height=44, color="#80cbc4", label="右"),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 05 · spacer")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(480, 100)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
