"""
Step 15：IME 中文输入 —— inputMethodEvent + 预编辑 + 粘贴。

运行：python demos/step15_ime.py

切换到中文输入法（如微软拼音），输入拼音选词上屏；
英文、Delete、Ctrl+V 仍可用。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Row, Text, TextInput, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 15 · IME")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())

    output = Text("（已上屏内容）", font_size=13)
    field_a = TextInput("", placeholder="中文 / 英文…", flex=1, min_width=160)
    field_b = TextInput("", placeholder="第二个输入框（测焦点切换）", flex=1)

    def refresh_output() -> None:
        output.set_text(f"框 A：{field_a.text!r}  |  框 B：{field_b.text!r}")
        canvas.repaint_node(output)

    def submit_a() -> None:
        refresh_output()

    def clear_a() -> None:
        field_a.text = ""
        field_a.cursor = 0
        field_a.clear_composition()
        field_a.mark_paint_dirty()
        canvas.repaint_node(field_a)
        refresh_output()

    field_a.on_submit = submit_a

    canvas.root = Column(
        padding=24,
        spacing=12,
        align="stretch",
        children=[
            Text("Step 15 · IME 中文输入", font_size=20, bold=True),
            Text(
                "切中文输入法 → 拼音预编辑（下划线）→ 选词上屏；"
                "Ctrl+V 粘贴；Delete 删光标后字符",
                font_size=12,
            ),
            field_a,
            field_b,
            Row(
                spacing=10,
                children=[
                    Button("读取 A 内容", on_click=refresh_output),
                    Button("清空 A", on_click=clear_a),
                ],
            ),
            output,
        ],
    )
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(520, 320)
    window.show()
    canvas.relayout(force=True)
    canvas._set_focus(field_a)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
