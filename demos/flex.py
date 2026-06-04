"""Demo 03 · flex：主轴剩余空间按比例分配。

运行（在 code/ui 目录下）：
    python demos/flex.py

验收点：
  - 拖动窗口宽度：中间 flex=1 的色块变宽，左右固定宽度不变
  - 无按钮、无交互，只看布局
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Row, Theme, run


@run(title="Demo 03 · flex", size=(480, 120), theme=Theme.dark())
class FlexDemo(App):
    def ui(self) -> None:
        self.root = Row(
            padding=20,
            spacing=8,
            align="stretch",
            nodes=[
                Box(width=56, height=48, color="#ffcdd2", label="56"),
                Box(flex=1, height=48, color="#bbdefb", label="flex=1"),
                Box(width=72, height=48, color="#c8e6c9", label="72"),
            ],
        )


if __name__ == "__main__":
    FlexDemo()
