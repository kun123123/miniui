"""Demo 10 · State + ForEach：改 State 自动重建列表。

运行（在 code/ui 目录下）：
    python demos/state.py

验收点：
  - 初始显示 3 条列表项（Box 行）
  - 点「添加一项」→ 列表多一行，无需手写 refresh
  - 使用 items.update() 原地 append 后通知订阅者
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Button, Column, DerivedText, ForEach, Theme, run


@run(title="Demo 10 · state", size=(360, 320), theme=Theme.dark())
class StateDemo(App):
    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.items = ctx.state(["苹果", "香蕉", "橙子"])

    def add_item(self) -> None:
        self.items.value.append(f"第 {len(self.items.value) + 1} 项")
        self.items.update()

    def item_row(self, name: str):
        return Box(height=40, label=name)

    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=12,
            nodes=[
                DerivedText(
                    lambda: f"共 {len(self.items.value)} 项",
                    deps=[self.items],
                    font_size=13,
                ),
                ForEach(self.items, self.item_row, spacing=8, scroll=False),
                Button("添加一项", on_click=self.add_item),
            ],
        )


if __name__ == "__main__":
    StateDemo()
