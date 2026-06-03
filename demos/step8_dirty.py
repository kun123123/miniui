"""
Step 8：脏标记 —— 布局脏才 relayout，仅外观变则局部重绘。

运行：python demos/step8_dirty.py

要点：
  - mark_layout_dirty() 沿 parent 冒泡到根
  - relayout() 在根未脏时直接跳过（看计数器）
  - mark_paint_dirty() + repaint_node() 只 update 节点矩形
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Row, Text, UiCanvas


def build_ui(canvas: UiCanvas) -> tuple[Column, Text]:
    content = Text("文案长度：短", font_size=15)
    stats = Text("relayout: 0  paint: 0", font_size=12)

    def refresh_stats(*, layout: bool = False) -> None:
        if layout:
            canvas.relayout()
        # 先写好文案再同步 repaint，避免 update() 异步导致计数「慢一拍」
        stats.text = (
            f"relayout={canvas.relayout_count}  "
            f"paint={canvas.paint_count + 1}"
        )
        stats.mark_paint_dirty()
        canvas.repaint()

    def lengthen() -> None:
        content.set_text(content.text + "～")
        canvas.relayout()
        refresh_stats()

    def noop_paint() -> None:
        """不改布局，只触发统计区重绘。"""
        refresh_stats()

    root = Column(
        padding=24,
        spacing=14,
        children=[
            Text("Step 8 · 脏标记", font_size=20, bold=True),
            Text(
                "加长文案 → layout_dirty → relayout；"
                "点按钮按下态 → 仅 repaint_node",
                font_size=13,
            ),
            content,
            stats,
            Row(
                spacing=12,
                children=[
                    Button("加长文案", on_click=lengthen),
                    Button("刷新统计", on_click=noop_paint),
                ],
            ),
            Text("观察：连按「刷新统计」relayout 不增，paint 会增加", font_size=11),
        ],
    )
    return root, stats


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 8 · MiniUI 脏标记")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())
    canvas.root, stats_line = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(520, 360)
    window.show()
    canvas.relayout(force=True)
    stats_line.text = (
        f"relayout={canvas.relayout_count}  paint={canvas.paint_count + 1}"
    )
    canvas.repaint()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
