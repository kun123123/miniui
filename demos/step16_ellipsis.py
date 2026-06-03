"""
Step 16：Text overflow —— visible / ellipsis / clip。

运行：python demos/step16_ellipsis.py

拖动窗口变窄：visible 溢出；ellipsis 显示 …；clip 硬截断。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Row, Text, UiCanvas

LONG = "这是一段非常非常非常非常非常非常非常非常长的待办标题"


def build_ui(canvas: UiCanvas) -> Column:
    hint = Text("拖动窗口边缘变窄，观察三种 overflow", font_size=12)

    def make_row(label: str, overflow: str) -> Row:
        return Row(
            spacing=8,
            children=[
                Text(f"{label}:", font_size=12),
                Text(LONG, font_size=13, flex=1, overflow=overflow),
                Button("×", on_click=lambda: None, min_width=32, height=28),
            ],
        )

    return Column(
        padding=24,
        spacing=12,
        align="stretch",
        children=[
            Text("Step 16 · Text overflow", font_size=20, bold=True),
            hint,
            make_row("visible", "visible"),
            make_row("ellipsis", "ellipsis"),
            make_row("clip", "clip"),
            Text(
                "Todo 行模拟（ellipsis + flex:1）",
                font_size=12,
            ),
            Row(
                spacing=8,
                children=[
                    Button("○", on_click=lambda: None, min_width=32, height=28),
                    Text(LONG, font_size=13, flex=1, overflow="ellipsis"),
                    Button("×", on_click=lambda: None, min_width=32, height=28),
                ],
            ),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 16 · ellipsis")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())
    canvas.root = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(560, 320)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
