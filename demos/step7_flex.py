"""
Step 7：flex:1、Spacer、margin。

运行：python demos/step7_flex.py

要点：
  - 子节点设 flex>0，在 Row/Column 主轴上按比例分剩余空间
  - Spacer(flex=1) 只占位、不绘制
  - margin 在节点外侧，与容器 padding 分开
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Column, Row, Spacer, Text, UiCanvas


def build_ui() -> Column:
    return Column(
        padding=16,
        spacing=12,
        children=[
            Text("Step 7 · flex / Spacer / margin", font_size=20, bold=True),
            Text("拖动窗口：右侧绿色区域随 flex:1 变宽", font_size=13),
            Row(
                flex=1,
                spacing=12,
                children=[
                    Box(
                        width=100,
                        label="侧栏 100px",
                        color="#ffe0b2",
                        margin=8,
                    ),
                    Box(flex=1, label="主区域 flex:1", color="#c8e6c9"),
                ],
            ),
            Row(
                spacing=8,
                children=[
                    Text("底栏", font_size=12),
                    Spacer(flex=1),
                    Text("Spacer 把这段文字顶到左侧", font_size=11),
                ],
            ),
        ],
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 7 · MiniUI flex 布局")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(build_ui())
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(560, 400)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
