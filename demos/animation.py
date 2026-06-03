"""动画：paint_dx/dy 偏移，不触发 relayout。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, Text, UiCanvas

SLIDE = 100.0


def main() -> None:
    app = QApplication(sys.argv)

    card = Row(
        spacing=10,
        align="center",
        children=[
            Box(width=48, height=48, color="#90caf9", label="块"),
            Text("动画只改 paint 偏移", font_size=13, flex=1),
        ],
    )

    def slide_in() -> None:
        card.paint_dx = -SLIDE
        canvas.animate_offset(card, dx=(-SLIDE, 0.0), duration=300)

    def bounce() -> None:
        canvas.animate_offset(
            card,
            dy=(0.0, -12.0),
            duration=120,
            on_finished=lambda: canvas.animate_offset(card, dy=(-12.0, 0.0), duration=160),
        )

    canvas = UiCanvas(
        Column(
            padding=20,
            spacing=12,
            children=[
                Text("animate_offset", font_size=16, bold=True),
                card,
                Row(spacing=8, children=[
                    Button("滑入", on_click=slide_in),
                    Button("弹跳", on_click=bounce),
                ]),
            ],
        )
    )

    window = QMainWindow()
    window.setWindowTitle("animation")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(400, 220)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
