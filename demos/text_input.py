"""Demo 07 · TextInput：点击聚焦、键盘输入、Enter 提交。

运行（在 code/ui 目录下）：
    python demos/text_input.py

验收点：
  - 点击输入框可聚焦，出现光标闪烁
  - 键盘输入文字，Backspace 删除
  - 回车后下方 Text 显示「提交：xxx」（on_submit）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Column, Text, TextInput, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    hint = Text("", font_size=13)

    draft = TextInput("", placeholder="在此输入，回车提交…", min_width=200)

    def submit() -> None:
        hint.set_text(f"提交：{draft.text!r}")

    draft.on_submit = submit

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=12,
            children=[draft, hint],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 07 · text_input")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(400, 140)
    window.show()
    canvas.relayout(force=True)
    canvas._set_focus(draft)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
