"""最小可运行应用：Column + Text + Button。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Text, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    def on_click() -> None:
        label.set_text("已点击")
        canvas.repaint_node(label)

    label = Text("Hello MiniUI", font_size=18, bold=True)
    canvas = UiCanvas(
        Column(
            padding=20,
            spacing=12,
            children=[
                label,
                Button("点我", on_click=on_click),
            ],
        )
    )

    window = QMainWindow()
    window.setWindowTitle("minimal_app")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 200)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
