"""Demo 12 · 换肤：canvas.set_theme 切换 light / dark，整窗重绘。

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

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Text, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    is_dark = [True]
    status = Text("当前：dark", font_size=14)

    def toggle_theme() -> None:
        is_dark[0] = not is_dark[0]
        canvas.set_theme(Theme.dark() if is_dark[0] else Theme.light())
        status.set_text(f"当前：{'dark' if is_dark[0] else 'light'}")

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=12,
            align="stretch",
            children=[
                status,
                Box(height=48, label="主题 box_fill"),
                Button("示例按钮"),
                Button("切换主题", on_click=toggle_theme),
            ],
        ),
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 12 · theme")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 260)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
