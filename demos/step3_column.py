"""
Step 3：Column 布局——spacing / padding 由 layout pass 自动计算。

目的：改 spacing=8 → spacing=24，子节点 y 坐标自动变，不用手写。
运行：python demos/step3_column.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Column, Text, UiCanvas


def build_ui() -> Column:
    return Column(
        padding=24,
        spacing=12,  # ← 改这个数字，看子节点间距变化
        children=[
            Text("Step 3 · Column 纵向布局", font_size=18, bold=True),
            Text("measure：每个孩子汇报需要多高", font_size=13),
            Text("layout：父节点按 spacing 分配 y", font_size=13),
            Box(height=64, color="#dce8ff", label="Box A"),
            Box(height=48, color="#ffe0e0", label="Box B"),
            Text("拖动窗口边缘可触发 relayout", font_size=12),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 3 · Column layout")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(build_ui())
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(520, 420)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
