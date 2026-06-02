"""
Step 5：完整示例——声明式 UI → measure → layout → paint。

运行：python demos/step5_app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, Text, UiCanvas


def build_ui() -> Column:
    """用户写的 UI 代码：只描述结构，不写坐标。"""
    return Column(
        padding=20,
        spacing=14,
        children=[
            Text("MiniUI 框架演示", font_size=20, bold=True),
            Text("你写的 Column / Row / Text 会先变成一棵树", font_size=13),
            Text("窗口 resize 时：measure → layout → 每个节点拿到 rect", font_size=13),
            Box(height=8, color="#eeeeee"),
            Row(
                spacing=12,
                children=[
                    Button("主要操作"),
                    Button("次要"),
                ],
            ),
            Column(
                padding=12,
                spacing=8,
                children=[
                    Text("嵌套 Column（带 padding=12）", font_size=13, bold=True),
                    Box(height=40, color="#e3f2fd", label="卡片区域"),
                    Box(height=40, color="#f3e5f5", label="卡片区域"),
                ],
            ),
            Text("拖动改变窗口大小，观察 layout 重算", font_size=11),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 5 · MiniUI 完整 demo")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(build_ui())
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(560, 520)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
