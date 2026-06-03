"""
Step 6：点击命中 + Button 回调 + 状态驱动重绘。

运行：python demos/step6_events.py

要点：
  - mousePressEvent → root.hit_test(x, y) 找到最上层节点
  - Button(on_click=...) 在 mouseRelease 且仍在按钮内时触发
  - 回调里改 Text.text，再 canvas.update() 触发 paint
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Row, Text, UiCanvas


def build_ui(canvas: UiCanvas) -> Column:
    status = Text("点击次数：0", font_size=16)
    count = {"n": 0}

    def increment() -> None:
        count["n"] += 1
        status.text = f"点击次数：{count['n']}"
        canvas.update()

    def reset() -> None:
        count["n"] = 0
        status.text = "点击次数：0"
        canvas.update()

    return Column(
        padding=24,
        spacing=16,
        children=[
            Text("Step 6 · 事件与状态", font_size=20, bold=True),
            Text("点击按钮 → hit_test → on_click → 改 text → update → paint", font_size=13),
            status,
            Row(
                spacing=12,
                children=[
                    Button("点我 +1", on_click=increment),
                    Button("重置", on_click=reset),
                ],
            ),
            Text("按住按钮时背景会加深（_pressed 状态）", font_size=11),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 6 · MiniUI 事件")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())
    canvas.root = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(480, 320)
    window.show()
    canvas.relayout()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
