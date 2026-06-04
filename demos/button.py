"""Demo 02 · Button：点击 + 属性变化自动重绘。

运行（在 code/ui 目录下）：
    python demos/button.py

验收点：
  - 按下按钮时背景变深（pressed 态）
  - 松开后文字变为「已点击」（set_text 自动重绘，无需手写 repaint_node）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Button, Column, Text, Theme, run


@run(title="Demo 02 · button", size=(360, 160), theme=Theme.dark())
class ButtonDemo(App):
    def on_click(self) -> None:
        self.ctx.label.set_text("已点击")

    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=12,
            nodes=[
                Text("点下面按钮", font_size=16, id="label"),
                Button("点我", on_click=self.on_click),
            ],
        )


if __name__ == "__main__":
    ButtonDemo()
