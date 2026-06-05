"""Demo 01 · 最小窗口 + 根 Text。

运行：python demos/minimal_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Column, Text, Theme, run


@run(title="Demo 01 · minimal", size=(400, 200), theme=Theme.dark())
class MinimalApp(App):
    def ui(self) -> None:
        self.root = Column(
            padding=20,
            nodes=[Text("Hello MiniUI")],
        )


if __name__ == "__main__":
    MinimalApp()
