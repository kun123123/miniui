"""Demo 07 · TextInput：点击聚焦、键盘输入、Enter 提交。

运行（在 code/ui 目录下）：
    python demos/text_input.py

验收点：
  - 点击输入框可聚焦，出现光标闪烁
  - 键盘输入文字，Backspace 删除
  - 回车后下方 Text 显示「提交：xxx」（on_submit）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Column, Text, TextInput, Theme, run


@run(title="Demo 07 · text_input", size=(400, 140), theme=Theme.dark())
class TextInputDemo(App):
    def submit(self) -> None:
        self.ctx.hint.set_text(f"提交：{self.ctx.draft.text!r}")

    def on_ready(self) -> None:
        self.ctx.canvas._set_focus(self.ctx.draft)

    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=12,
            nodes=[
                TextInput(
                    "",
                    placeholder="在此输入，回车提交…",
                    min_width=200,
                    id="draft",
                    on_submit=self.submit,
                ),
                Text("", font_size=13, id="hint"),
            ],
        )


if __name__ == "__main__":
    TextInputDemo()
