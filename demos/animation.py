"""Demo 11 · animate_offset：paint_dx/dy 偏移动画，不改变 layout。

运行（在 code/ui 目录下）：
    python demos/animation.py

验收点：
  - 点击按钮：色块沿水平方向平滑滑出 / 滑回
  - layout 槽位不变（拖动窗口时色块仍占原行宽）
  - 仅改 paint_dx，不 relayout
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Button, Column, Text, Theme, run

SLIDE = 100.0


@run(title="Demo 11 · animation", size=(400, 200), theme=Theme.dark())
class AnimationDemo(App):
    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.busy = False

    def toggle(self) -> None:
        if self.busy:
            return
        box = self.ctx.box
        self.busy = True
        at_rest = abs(box.paint_dx) < 1
        dx = (0.0, SLIDE) if at_rest else (box.paint_dx, 0.0)

        def done() -> None:
            self.busy = False

        self.ctx.animate("box", dx=dx, duration=400, on_finished=done)

    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=12,
            align="stretch",
            nodes=[
                Text("点击按钮：色块滑动，布局槽位保持不动", font_size=13),
                Box(height=56, color="#90caf9", label="paint_dx", id="box"),
                Button("右移 / 复位", on_click=self.toggle),
            ],
        )


if __name__ == "__main__":
    AnimationDemo()
