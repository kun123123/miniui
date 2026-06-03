"""
Step 11：ScrollView —— 裁剪 + scroll_y + 滚轮。

运行：python demos/step11_scroll.py

要点：
  - 内容 Column 高度可大于视口
  - paint：setClipRect + translate(-scroll_y)
  - hit_test / wheel：坐标加 scroll_y 转换
  - 列表项改为 Button，滚动后点击验证 hit_test
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Row, ScrollView, Text, UiCanvas


def build_ui(canvas: UiCanvas) -> Column:
    list_col = Column(spacing=8, padding=4)
    hint = Text("滚动后点击列表中的按钮", font_size=11)

    def on_item_click(index: int) -> None:
        def handler() -> None:
            hint.text = (
                f"点击了条目 {index}  "
                f"scroll_y={scroll.scroll_y:.0f}  "
                f"共 {len(list_col.children)} 条"
            )
            canvas.repaint()

        return handler

    for i in range(1, 16):
        list_col.add_child(
            Button(f"条目 {i} — 点我", on_click=on_item_click(i), min_width=200)
        )

    scroll = ScrollView(list_col, flex=1)

    def add_more() -> None:
        n = len(list_col.children) + 1
        list_col.add_child(
            Button(f"条目 {n}（新加）", on_click=on_item_click(n), min_width=200)
        )
        scroll.mark_layout_dirty()
        canvas.relayout()
        scroll.scroll_by(1e9)
        canvas.update()
        hint.text = f"共 {len(list_col.children)} 条，scroll_y={scroll.scroll_y:.0f}"
        canvas.repaint()

    def remove_more() -> None:
        if not list_col.children:
            return
        list_col.remove_child(list_col.children[-1])
        scroll.mark_layout_dirty()
        canvas.relayout()
        canvas.update()
        hint.text = f"共 {len(list_col.children)} 条，scroll_y={scroll.scroll_y:.0f}"
        canvas.repaint()

    return Column(
        padding=20,
        spacing=12,
        children=[
            Text("Step 11 · ScrollView", font_size=20, bold=True),
            Text(
                "滚轮浏览列表，点击条目按钮；hit_test 会加 scroll_y 换算坐标",
                font_size=13,
            ),
            scroll,
            hint,
            Row(
                spacing=10,
                children=[
                    Button("再加一条", on_click=add_more),
                    Button("再减一条", on_click=remove_more),
                ],
            ),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 11 · MiniUI 滚动")
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
