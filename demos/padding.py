"""Demo 04 · padding / spacing：容器内边距与子项间距。

运行（在 code/ui 目录下）：
    python demos/padding.py

验收点：
  - 色块与窗口边缘之间有明显留白（padding=32）
  - 三个色块之间的缝隙等宽（spacing=24）
  - 拖动窗口：留白与缝隙大小不变，只有色块横向变宽
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Column, Theme, UiCanvas

PADDING = 32
SPACING = 24


def main() -> None:
    app = QApplication(sys.argv)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=PADDING,
            spacing=SPACING,
            children=[
                Box(height=48, color="#ffccbc", label=f"padding={PADDING}"),
                Box(height=48, color="#b3e5fc", label=f"spacing={SPACING}"),
                Box(height=48, color="#c5e1a5", label="子项 C"),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 04 · padding")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(400, 280)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
