"""
Step 14：局部重绘 —— paint_dirty + event.rect() 只画脏子树。

运行：python demos/step14_partial_paint.py

要点：
  - repaint_node 传入 Qt 脏矩形
  - paintEvent 用 paint_region 剪枝，只绘制 dirty 且相交的节点
  - 观察 full / partial / nodes_painted 计数
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Row, Text, TextInput, UiCanvas


class CountingText(Text):
    """每次 paint 自增，用于观察静态区是否被误重绘。"""

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(text, **kwargs)
        self.paint_calls = 0

    def paint(self, painter: QPainter) -> None:
        self.paint_calls += 1
        super().paint(painter)


def build_ui(canvas: UiCanvas) -> tuple[Column, Text, list[CountingText]]:
    static_lines = [
        CountingText(f"静态行 {i:02d} · 不应因按钮按下而重绘", font_size=12)
        for i in range(1, 16)
    ]
    first_static = static_lines[0]
    stats = Text("", font_size=12)
    field = TextInput("", placeholder="打字 / 光标闪烁 → partial", flex=1)

    def refresh_stats() -> None:
        static_paints = sum(t.paint_calls for t in static_lines)
        stats.set_text(
            f"full={canvas.full_paint_count}  "
            f"partial={canvas.partial_paint_count}  "
            f"nodes={canvas.nodes_painted_last}  "
            f"relayout={canvas.relayout_count}  "
            f"static_paints={static_paints}"
        )
        canvas.repaint_node(stats)

    def lengthen_static() -> None:
        first_static.set_text(first_static.text + "～")
        canvas.relayout()
        canvas.repaint()
        refresh_stats()

    root = Column(
        padding=20,
        spacing=10,
        children=[
            Text("Step 14 · 局部重绘", font_size=20, bold=True),
            Text(
                "按下按钮 / 输入 / 光标闪 → partial，nodes≈1；"
                "加长静态行 → relayout + full",
                font_size=12,
            ),
            stats,
            Row(
                spacing=10,
                children=[
                    Button("闪按钮 A", on_click=refresh_stats),
                    Button("闪按钮 B", on_click=refresh_stats),
                    field,
                ],
            ),
            Button("加长首行静态文案（触发布局）", on_click=lengthen_static),
            Column(flex=1, spacing=4, padding=12, children=static_lines),
        ],
    )
    return root, stats, static_lines


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 14 · MiniUI 局部重绘")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())
    canvas.root, stats_line, static_lines = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(520, 520)
    window.show()
    canvas.relayout(force=True)
    canvas.repaint()
    static_paints = sum(t.paint_calls for t in static_lines)
    stats_line.set_text(
        f"full={canvas.full_paint_count}  "
        f"partial={canvas.partial_paint_count}  "
        f"nodes={canvas.nodes_painted_last}  "
        f"relayout={canvas.relayout_count}  "
        f"static_paints={static_paints}"
    )
    canvas.repaint_node(stats_line)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
