"""Demo 02 · Button：点击 + 属性变化自动重绘。

运行（在 code/ui 目录下）：
    python demos/button.py

验收点：
  - 按下按钮时背景变深（pressed 态）
  - 松开后文字变为「已点击」（set_text 自动重绘，无需手写 repaint_node）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Text, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    label = Text("点下面按钮", font_size=16)

    def on_click() -> None:
        label.set_text("已点击")

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=12,
            children=[
                label,
                Button("点我", on_click=on_click),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 02 · button")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 160)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
