"""控件：Text / Box / Button / TextInput。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, Text, TextInput, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)
    hint = Text("", font_size=12)
    draft = TextInput("", placeholder="输入后回车…", flex=1)

    def submit() -> None:
        hint.set_text(f"提交：{draft.text!r}")
        canvas.repaint_node(hint)

    draft.on_submit = submit

    canvas = UiCanvas(
        Column(
            padding=16,
            spacing=10,
            children=[
                Text("控件示例", font_size=16, bold=True),
                Box(height=40, color="#e3f2fd", label="Box 色块"),
                Text("长标题会被省略…", font_size=13, flex=1, overflow="ellipsis"),
                Row(spacing=8, children=[draft, Button("提交", on_click=submit)]),
                hint,
            ],
        ),
        theme=Theme.light(),
    )

    window = QMainWindow()
    window.setWindowTitle("widgets")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(420, 260)
    window.show()
    canvas._set_focus(draft)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
