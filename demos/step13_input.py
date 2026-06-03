"""
Step 13：TextInput —— 焦点 + 键盘输入 + 光标。

运行：python demos/step13_input.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Text, TextInput, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 13 · TextInput")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())

    output = Text("（输出）", font_size=13)
    field = TextInput("", placeholder="在此输入…", flex=1, min_width=200)

    def submit() -> None:
        output.text = f"你输入了：{field.text!r}"
        canvas.repaint()

    field.on_submit = submit

    canvas.root = Column(
        padding=24,
        spacing=12,
        align="stretch",
        children=[
            Text("Step 13 · TextInput", font_size=20, bold=True),
            Text("点击输入框聚焦，打字，回车提交", font_size=13),
            field,
            Button("提交", on_click=submit),
            output,
        ],
    )
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(440, 220)
    window.show()
    canvas._set_focus(field)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
