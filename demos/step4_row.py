"""
Step 4：Row 横向布局 + Column 嵌套。

运行：python demos/step4_row.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Row, Text, UiCanvas


def build_ui() -> Column:
    return Column(
        padding=24,
        spacing=16,
        children=[
            Text("Step 4 · Row + Column 嵌套", font_size=18, bold=True),
            Text("Row 的 spacing 控制按钮之间的水平距离", font_size=13),
            Row(
                spacing=16,
                children=[
                    Button("确定"),
                    Button("取消"),
                    Button("帮助"),
                ],
            ),
            Text("下面 Row align=center，竖直居中", font_size=13),
            Row(
                spacing=8,
                align="center",
                children=[
                    Button("A"),
                    Button("B"),
                ],
            ),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(build_ui())
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(520, 360)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
