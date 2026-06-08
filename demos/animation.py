"""Demo 11 · animate_sentence：点击按钮，连续执行多步动画。

运行（在 code/ui 目录下）：
    python demos/animation.py

验收点：
  - 点击「播放」：三个色块依次右移，再依次滑回
  - 动画播放中按钮禁用，防止重复触发
  - layout 槽位不变，仅 paint_dx/dy 偏移
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import AnimStep, App, Box, Button, Column, DerivedText, Row, Text, Theme, run

SLIDE = 72.0


@run(title="Demo 11 · animation", size=(420, 260), theme=Theme.dark())
class AnimationDemo(App):
    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.busy = ctx.state(False)
        self.hint = ctx.state("点击「播放」开始连续动画")

    def play(self) -> None:
        if self.busy.value:
            return
        self.busy.set(True)
        self.hint.set("播放中…")

        def done() -> None:
            self.busy.set(False)
            self.hint.set("播放完成，可再次点击")

        self.ctx.animate_sentence(
            [
                AnimStep("a", dx=SLIDE, duration=280),
                AnimStep("b", dx=SLIDE, duration=280),
                AnimStep("c", dx=SLIDE, duration=280),
                AnimStep("a", dx=0, duration=280),
                AnimStep("b", dx=0, duration=280),
                AnimStep("c", dx=0, duration=280),
            ],
            on_finished=done,
        )

    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=14,
            align="stretch",
            nodes=[
                Text("连续动画：animate_sentence", font_size=15, bold=True),
                DerivedText(lambda: self.hint.value, deps=[self.hint], font_size=13),
                Row(
                    spacing=10,
                    align="center",
                    nodes=[
                        Box(width=56, height=56, color="#ef5350", label="A", id="a"),
                        Box(width=56, height=56, color="#66bb6a", label="B", id="b"),
                        Box(width=56, height=56, color="#42a5f5", label="C", id="c"),
                    ],
                ),
                Button(
                    "播放",
                    on_click=self.play,
                    id="play_btn",
                ),
            ],
        )


if __name__ == "__main__":
    AnimationDemo()
