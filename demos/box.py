"""Demo 06 · Box：圆角色块（color / radius / label）。

运行（在 code/ui 目录下）：
    python demos/box.py

验收点：
  - 三个色块：自定义颜色、圆角、标签文字
  - 第三个不传 color，使用主题默认 box_fill
  - 无交互，只展示 Box 绘制
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Column, Theme, run


@run(title="Demo 06 · box", size=(320, 240), theme=Theme.dark())
class BoxDemo(App):
    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=12,
            nodes=[
                Box(
                    width=220,
                    height=52,
                    color="#ef9a9a",
                    radius=12,
                    label="color + radius=12",
                ),
                Box(
                    width=220,
                    height=52,
                    color="#90caf9",
                    label="color + label",
                ),
                Box(width=220, height=52, label="theme default"),
            ],
        )


if __name__ == "__main__":
    BoxDemo()
