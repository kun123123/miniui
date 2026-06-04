"""Demo · TextArea：多行输入、换行、滚动、Ctrl+Enter 提交。

运行（在 code/ui 目录下）：
    python demos/text_area.py

验收点：
  - 点击文本区聚焦，光标闪烁
  - Enter 硬换行；超宽自动软换行（拖窄窗口可见）
  - 行数超出视口时滚轮纵向滚动
  - Ctrl+Enter 后下方 Text 显示提交内容（含换行）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Column, Text, TextArea, Theme, run


@run(title="Demo · text_area", size=(480, 320), theme=Theme.dark())
class TextAreaDemo(App):
    def submit(self) -> None:
        body = self.ctx.body.text
        lines = body.count("\n") + 1 if body else 0
        preview = body.replace("\n", "\\n")
        if len(preview) > 80:
            preview = preview[:77] + "…"
        self.ctx.hint.set_text(f"提交（{lines} 行）：{preview!r}")

    def on_ready(self) -> None:
        self.ctx.canvas._set_focus(self.ctx.body)

    def ui(self) -> None:
        self.root = Column(
            padding=20,
            spacing=10,
            align="stretch",
            nodes=[
                Text(
                    "Enter 硬换行 · 超宽自动折行 · ↑↓ 移行 · Ctrl+Enter 提交",
                    font_size=12,
                ),
                TextArea(
                    "第一行\n第二行\n这是一段很长的文字会在框变窄时自动折成多行显示",
                    placeholder="在此输入多行正文…",
                    flex=1,
                    min_lines=8,
                    id="body",
                    on_submit=self.submit,
                ),
                Text("", font_size=12, id="hint"),
            ],
        )


if __name__ == "__main__":
    TextAreaDemo()
