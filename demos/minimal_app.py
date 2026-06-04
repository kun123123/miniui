"""Demo 01 · 最小可运行：Qt 窗口 + UiCanvas + 单个 Text。

运行（在 code/ui 目录下）：
    python demos/minimal_app.py

验收点：
  - 窗口中央显示一行静态文字
  - 无 Column / Button，只有根节点 Text 占满画布
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Text, Theme, run


@run(title="Demo 01 · minimal_app", size=(360, 120), theme=Theme.dark())
class MinimalApp(App):
    def ui(self) -> None:
        self.root = Text("MiniUI · minimal_app", font_size=20)


if __name__ == "__main__":
    MinimalApp()
