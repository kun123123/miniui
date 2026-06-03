"""布局：Column / Row / Spacer / flex / margin。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Column, Row, Spacer, Text, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    root = Column(
        padding=16,
        spacing=10,
        children=[
            Text("Row + flex", font_size=16, bold=True),
            Row(
                spacing=8,
                flex=1,
                children=[
                    Box(width=80, height=48, color="#ffe0b2", label="固定宽"),
                    Box(flex=1, height=48, color="#c8e6c9", label="flex:1"),
                ],
            ),
            Row(spacing=8, children=[
                Text("左", font_size=12),
                Spacer(flex=1),
                Text("右（Spacer 顶开）", font_size=12),
            ]),
        ],
    )

    canvas = UiCanvas(root)
    window = QMainWindow()
    window.setWindowTitle("layout")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(480, 280)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
