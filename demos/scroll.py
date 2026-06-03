"""ScrollView：长列表 + 滚轮（自动处理，无需手写 scroll_y）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, ScrollView, Text, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)
    canvas = UiCanvas(Column())

    list_col = Column(spacing=6, padding=4)
    for i in range(1, 21):
        list_col.add_child(Button(f"条目 {i}", min_width=160))

    scroll = ScrollView(list_col, flex=1)
    canvas.root = Column(
        padding=16,
        spacing=10,
        children=[
            Text("滚轮浏览列表", font_size=16, bold=True),
            scroll,
        ],
    )

    window = QMainWindow()
    window.setWindowTitle("scroll")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 320)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
