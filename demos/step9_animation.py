"""
Step 9：rect 动画 —— layout 定槽位，paint 偏移在动。

运行：python demos/step9_animation.py

要点：
  - layout 后的 rect 是「槽位」（参与 hit_test）
  - paint_dx / paint_dy 是绘制偏移（QPropertyAnimation 逐帧改）
  - 动画期间不 relayout，只 update() 重绘
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, Text, UiCanvas

SLIDE = 160.0


def build_ui(canvas: UiCanvas) -> Column:
    card = Box(height=72, color="#bbdefb", label="我会滑动")

    def slide_in() -> None:
        card.paint_dx = -SLIDE
        canvas.animate_offset(card, dx=(-SLIDE, 0.0), duration=400)

    def slide_out() -> None:
        canvas.animate_offset(
            card,
            dx=(card.paint_dx, -SLIDE),
            duration=400,
            on_finished=card.reset_paint_offset,
        )

    def bounce() -> None:
        canvas.animate_offset(
            card,
            dy=(0.0, -28.0),
            duration=180,
            on_finished=lambda: canvas.animate_offset(
                card, dy=(-28.0, 0.0), duration=220
            ),
        )

    return Column(
        padding=24,
        spacing=16,
        children=[
            Text("Step 9 · rect 动画", font_size=20, bold=True),
            Text(
                "蓝色块 layout 槽位不变；paint_dx/dy 由 QPropertyAnimation 驱动",
                font_size=13,
            ),
            card,
            Row(
                spacing=10,
                children=[
                    Button("滑入", on_click=slide_in),
                    Button("滑出", on_click=slide_out),
                    Button("弹跳", on_click=bounce),
                ],
            ),
            Text("hit_test 仍按 layout rect，动画时点击槽位区域有效", font_size=11),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 9 · MiniUI 动画")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())
    canvas.root = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(480, 320)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
