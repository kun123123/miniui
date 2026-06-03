"""
Step 17：Theme —— 浅色 / 深色一键切换。

运行：python demos/step17_theme.py

换肤只 repaint，不 relayout。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, Text, TextInput, Theme, UiCanvas


def build_ui(canvas: UiCanvas) -> tuple[Column, Text]:
    state = {"dark": False}
    status = Text("当前：浅色", font_size=12)
    field = TextInput("", placeholder="输入点什么…", flex=1)

    def refresh_status() -> None:
        name = "深色" if state["dark"] else "浅色"
        status.set_text(f"当前：{name}")
        canvas.repaint_node(status)

    def toggle_theme() -> None:
        state["dark"] = not state["dark"]
        canvas.set_theme(Theme.dark() if state["dark"] else Theme.light())
        refresh_status()

    root = Column(
        padding=24,
        spacing=12,
        align="stretch",
        children=[
            Text("Step 17 · Theme", font_size=20, bold=True),
            Text("点击按钮切换浅色 / 深色；只重绘，不重新布局", font_size=12),
            Row(
                spacing=10,
                children=[
                    Button("切换主题", on_click=toggle_theme),
                    status,
                ],
            ),
            field,
            Row(
                spacing=10,
                children=[
                    Button("次要操作", on_click=lambda: None),
                    Button("主要操作", on_click=lambda: None),
                ],
            ),
            Box(label="Box 跟随主题", height=48),
            Box(color="#5a8a6a", label="自定义色 Box 不变", height=48),
        ],
    )
    return root, status


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 17 · Theme")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column(), theme=Theme.light())
    canvas.root, _ = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(520, 360)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
