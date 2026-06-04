"""Demo 14 · split_column：Row 里两列都是 flex=1，平分剩余宽度。

运行（在 code/ui 目录下）：
    python demos/split_column.py

验收点：
  - 初始两列宽度大致相等（各 flex=1）
  - 点「侧栏加字」：列宽仍各占一半，长文用 ellipsis 截断，不会挤占另一列
  - 拖动窗口：两列仍按 flex 比例一起变宽/变窄
  - 点「主区换色」：只重绘，列宽不变
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Button, Column, Row, Text, Theme, run

_COLORS = ("#1565c0", "#6a1b9a", "#2e7d32", "#ef6c00")


@run(title="Demo 14 · split_column", size=(560, 300), theme=Theme.dark())
class SplitColumnDemo(App):
    def mount(self, ctx) -> None:
        super().mount(ctx)
        self._chars = 2
        self._color_idx = 0
        self._side_col: Column | None = None
        self._main_col: Column | None = None
        self._hint: Text | None = None

    def _sync_sizes(self) -> None:
        if self._hint is None or self._side_col is None or self._main_col is None:
            return
        sw = self._side_col.rect.width
        mw = self._main_col.rect.width
        self._hint._text = (
            f"侧栏列 {sw:.0f}px · 主区列 {mw:.0f}px（flex=1 时应大致相等）"
        )
        self._hint._display_key = None
        self._hint.mark_paint_dirty()

    def widen_sidebar(self) -> None:
        self._chars += 1
        self.side_label.text = "侧栏 " + "字" * self._chars
        canvas = self.ctx.canvas
        if canvas is not None:
            canvas.relayout()
        self._sync_sizes()

    def recolor_main(self) -> None:
        self._color_idx = (self._color_idx + 1) % len(_COLORS)
        self.main_box.color = _COLORS[self._color_idx]
        self._sync_sizes()

    def ui(self) -> None:
        self.side_label = Text(
            "侧栏 " + "字" * self._chars, font_size=15, overflow="ellipsis"
        )
        self._hint = Text("", font_size=12, overflow="ellipsis")
        self.main_box = Box(
            flex=1,
            height=100,
            color=_COLORS[0],
            label="剩余宽度都给这里",
        )

        self._side_col = Column(
            flex=1,
            padding=16,
            spacing=10,
            nodes=[
                Text("侧栏列 flex=1", font_size=13, bold=True),
                self.side_label,
                Button("侧栏加字 (layout)", on_click=self.widen_sidebar),
            ],
        )
        self._main_col = Column(
            flex=1,
            padding=16,
            spacing=10,
            align="stretch",
            nodes=[
                Text("主区列 flex=1", font_size=13, bold=True),
                self.main_box,
                Button("主区换色 (paint)", on_click=self.recolor_main),
                self._hint,
            ],
        )
        self.root = Row(align="stretch", nodes=[self._side_col, self._main_col])

    def on_ready(self) -> None:
        canvas = self.ctx.canvas
        if canvas is not None:
            canvas.relayout()
        self._sync_sizes()


if __name__ == "__main__":
    SplitColumnDemo()
