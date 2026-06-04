"""Demo 12 · 换肤：set_theme 切换 light / dark，整窗重绘。

运行（在 code/ui 目录下）：
    python demos/theme.py

验收点：
  - 启动为 dark，Text / Button / Box 使用主题色
  - 点「切换主题」→ light，背景与控件配色整体变化
  - 再点切回 dark；不 relayout，只整窗重绘
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Box, Button, Column, DerivedText, Theme, run


@run(title="Demo 12 · theme", size=(360, 260), theme=Theme.dark())
class ThemeDemo(App):
    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.is_dark = ctx.state(True)

    def toggle_theme(self) -> None:
        self.is_dark.set(not self.is_dark.value)
        self.ctx.set_theme(Theme.dark() if self.is_dark.value else Theme.light())

    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=12,
            align="stretch",
            nodes=[
                DerivedText(
                    lambda: f"当前：{'dark' if self.is_dark.value else 'light'}",
                    deps=[self.is_dark],
                    font_size=14,
                ),
                Box(height=48, label="主题 box_fill"),
                Button("示例按钮"),
                Button("切换主题", on_click=self.toggle_theme),
            ],
        )


if __name__ == "__main__":
    ThemeDemo()
