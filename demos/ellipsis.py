"""Demo 08 · Text 省略号：overflow='ellipsis' 在宽度不足时末尾显示 …。

运行（在 code/ui 目录下）：
    python demos/ellipsis.py

验收点：
  - 窗口较宽时，长文本完整显示
  - 拖动变窄后，末尾变为 …（Qt ElideRight）
  - 仅演示 ellipsis，无其它 overflow 模式
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Column, Text, Theme, UiCanvas

LONG_TEXT = (
    "这是一段很长的文本，用来演示 Text 的 overflow='ellipsis'："
    "当布局宽度不够时，绘制串会被截断并在末尾显示省略号。"
)


def main() -> None:
    app = QApplication(sys.argv)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=16,
            align="stretch",
            children=[
                Text("拖动窗口变窄，观察下方长文本末尾 …", font_size=13),
                Text(LONG_TEXT, overflow="ellipsis"),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 08 · ellipsis")
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
