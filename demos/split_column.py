"""Demo 14 · 两列 flex=1 平分；layout vs paint 脏标记。

运行：python demos/split_column.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Button, Column, DerivedText, Row, Text, Theme, run


@run(title="Demo 14 · split_column", size=(560, 280), theme=Theme.dark())
class SplitColumnDemo(App):
    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.sidebar_text = ctx.state("侧栏短标题")

    def lengthen(self) -> None:
        self.sidebar_text.set(
            self.sidebar_text.value
            + " · 再加一段很长很长很长很长很长很长的文字"
        )

    def ui(self) -> None:
        self.root = Column(
            padding=16,
            spacing=12,
            nodes=[
                Text("两列都 flex=1：侧栏加字不应挤窄主区", font_size=13),
                Row(
                    spacing=12,
                    align="stretch",
                    flex=1,
                    nodes=[
                        Column(
                            flex=1,
                            spacing=8,
                            nodes=[
                                Text("侧栏", font_size=12),
                                DerivedText(
                                    lambda: self.sidebar_text.value,
                                    deps=[self.sidebar_text],
                                    overflow="ellipsis",
                                ),
                                Button("侧栏加字", on_click=self.lengthen),
                            ],
                        ),
                        Column(
                            flex=1,
                            spacing=8,
                            nodes=[
                                Text("主区", font_size=12),
                                Text(
                                    "主区宽度应始终与侧栏各占一半。"
                                    "侧栏文案变长只会 ellipsis，不会抢宽。",
                                    overflow="ellipsis",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )


if __name__ == "__main__":
    SplitColumnDemo()
