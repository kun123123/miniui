"""Demo 09 · ScrollView：内容高于视口时滚轮滚动。

运行（在 code/ui 目录下）：
    python demos/scroll.py

验收点：
  - 下方列表项总高度大于可视区域，超出部分被裁剪
  - 鼠标在滚动区内滚轮：列表上下移动，scroll_y 变化
  - 滚到顶/底时不再越界
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Column, ScrollView, Text, Theme, run

ITEMS = 12
COLORS = ("#ffcdd2", "#f8bbd0", "#e1bee7", "#c5cae9", "#bbdefb", "#b2dfdb")


@run(title="Demo 09 · scroll", size=(360, 280), theme=Theme.dark())
class ScrollDemo(App):
    def ui(self) -> None:
        list_column = Column(
            spacing=8,
            align="stretch",
            nodes=[
                Box(height=48, color=COLORS[i % len(COLORS)], label=f"第 {i + 1} 项")
                for i in range(ITEMS)
            ],
        )
        self.root = Column(
            padding=20,
            spacing=12,
            nodes=[
                Text("滚轮在下方区域滚动列表", font_size=13),
                ScrollView(flex=1, child=list_column),
            ],
        )


if __name__ == "__main__":
    ScrollDemo()
