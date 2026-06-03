"""Demo 10 · State + Bindings.list：改 State 自动重建列表。

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

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Bindings, Box, Button, Column, State, Text, Theme, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)

    items = State(["苹果", "香蕉", "橙子"])
    list_col = Column(spacing=8, align="stretch")
    count_label = Text("", font_size=13)

    def add_item() -> None:
        items.value.append(f"第 {len(items.value) + 1} 项")
        items.update()

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Column(
            padding=20,
            spacing=12,
            children=[
                count_label,
                list_col,
                Button("添加一项", on_click=add_item),
            ],
        ),
    )

    bindings = Bindings(canvas)
    bindings.text(count_label, lambda: f"共 {len(items.value)} 项", items)
    bindings.list(
        list_col,
        lambda: items.value,
        lambda name: Box(height=40, label=name),
        items,
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 10 · state")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 320)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
