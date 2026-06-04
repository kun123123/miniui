"""Demo 05 · Spacer：吃掉 Row 主轴剩余空间。

运行（在 code/ui 目录下）：
    python demos/spacer.py

验收点：
  - 左右两个色块宽度固定，始终贴在 Row 两侧（中间 Spacer 撑开）
  - 拖动窗口变宽：只有中间空白变宽，色块宽度不变
  - Spacer 本身不可见、不绘制
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Row, Spacer, Theme, run


@run(title="Demo 05 · spacer", size=(480, 100), theme=Theme.dark())
class SpacerDemo(App):
    def ui(self) -> None:
        self.root = Row(
            padding=20,
            align="center",
            nodes=[
                Box(width=80, height=44, color="#ffab91", label="左"),
                Spacer(flex=1),
                Box(width=80, height=44, color="#80cbc4", label="右"),
            ],
        )


if __name__ == "__main__":
    SpacerDemo()
