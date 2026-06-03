"""Demo 01 · 最小可运行：Qt 窗口 + UiCanvas + 单个 Text。

运行（在 code/ui 目录下）：
    python demos/minimal_app.py

验收点：
  - 窗口中央显示一行静态文字
  - 无 Column / Button，只有根节点 Text 占满画布
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Text, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Text("MiniUI · minimal_app", font_size=20),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 01 · minimal_app")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 120)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
