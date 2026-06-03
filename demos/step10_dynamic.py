"""
Step 10：动态增删子节点 —— 串联 Step 6～9。

运行：python demos/step10_dynamic.py

要点：
  - Column.add_child / remove_child → mark_layout_dirty
  - relayout 重算整列 → repaint 显示新结构
  - 新条目 slide-in；删除前先 slide-out 再 remove
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, Text, UiCanvas

SLIDE = 120.0
COLORS = ("#c8e6c9", "#ffe0b2", "#e1bee7", "#b3e5fc", "#f0f4c3")


def build_ui(canvas: UiCanvas) -> Column:
    counter = {"n": 0}
    list_col = Column(flex=1, spacing=8, padding=8)
    status = Text("共 0 条", font_size=12)

    def refresh_status() -> None:
        status.text = f"共 {len(list_col.children)} 条"
        status.mark_paint_dirty()
        canvas.repaint()

    def add_item() -> None:
        counter["n"] += 1
        n = counter["n"]
        item = Box(
            height=44,
            color=COLORS[(n - 1) % len(COLORS)],
            label=f"条目 {n}",
        )
        list_col.add_child(item)
        canvas.relayout()
        item.paint_dx = -SLIDE
        canvas.animate_offset(item, dx=(-SLIDE, 0.0), duration=320)
        refresh_status()

    def remove_last() -> None:
        if not list_col.children:
            return
        item = list_col.children[-1]

        def _done() -> None:
            list_col.remove_child(item)
            item.reset_paint_offset()
            canvas.relayout()
            canvas.repaint()
            refresh_status()

        canvas.animate_offset(
            item,
            dx=(item.paint_dx, -SLIDE),
            duration=280,
            on_finished=_done,
        )

    return Column(
        padding=20,
        spacing=12,
        children=[
            Text("Step 10 · 动态列表", font_size=20, bold=True),
            Text(
                "增删 children → layout_dirty → relayout；新项带滑入动画",
                font_size=13,
            ),
            list_col,
            status,
            Row(
                spacing=10,
                children=[
                    Button("添加条目", on_click=add_item),
                    Button("删除最后", on_click=remove_last),
                ],
            ),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 10 · MiniUI 动态树")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())
    canvas.root = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(480, 420)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
