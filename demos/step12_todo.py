"""
Step 12：综合 Todo —— 串联 Step 6～11 + TextInput。

运行：python demos/step12_todo.py

在底部输入框打字，回车或点「添加」写入列表；点击输入框聚焦。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, ScrollView, Text, TextInput, UiCanvas


def build_ui(canvas: UiCanvas) -> tuple[Column, TextInput]:
    items: list[dict] = []
    todos_col = Column(spacing=6, padding=4)
    scroll = ScrollView(todos_col, flex=1)
    stats = Text("", font_size=12)
    draft = TextInput(
        "",
        placeholder="输入待办，回车添加…",
        flex=1,
        min_width=160,
    )

    def refresh_stats() -> None:
        pending = sum(1 for it in items if not it["state"]["done"])
        stats.set_text(f"{pending} 项待办 / 共 {len(items)} 项")
        canvas.repaint()

    def make_todo(label: str) -> Row:
        state = {"done": False}
        text = Text(label, font_size=13, flex=1, overflow="ellipsis")
        holder: dict = {}

        def toggle() -> None:
            state["done"] = not state["done"]
            prefix = "✓ " if state["done"] else ""
            text.set_text(prefix + label)
            canvas.relayout()
            canvas.repaint()
            refresh_stats()

        def remove() -> None:
            todos_col.remove_child(holder["row"])
            items[:] = [it for it in items if it["row"] is not holder["row"]]
            canvas.relayout()
            canvas.repaint()
            refresh_stats()

        row = Row(
            spacing=8,
            children=[
                Button("○", on_click=toggle, min_width=32, height=28),
                text,
                Button("×", on_click=remove, min_width=32, height=28),
            ],
        )
        holder["row"] = row
        items.append({"state": state, "row": row})
        return row

    def add_todo() -> None:
        label = draft.text.strip()
        if not label:
            return
        todos_col.add_child(make_todo(label))
        draft.text = ""
        draft.cursor = 0
        canvas.relayout()
        scroll.scroll_by(1e9)
        canvas.update()
        canvas._set_focus(draft)
        refresh_stats()

    draft.on_submit = add_todo

    return (
        Column(
        spacing=0,
        children=[
            Row(
                flex=1,
                align="stretch",
                children=[
                    Box(width=96, color="#455a64", label="Todo\nMiniUI"),
                    Column(
                        flex=1,
                        padding=16,
                        spacing=10,
                        children=[
                            Text("Step 12 · 综合 Todo", font_size=18, bold=True),
                            Text("TextInput 输入 + 滚动列表 + 按钮", font_size=12),
                            stats,
                            scroll,
                            Row(
                                spacing=8,
                                children=[
                                    draft,
                                    Button("添加", on_click=add_todo, min_width=64),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
        draft,
    )


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Step 12 · MiniUI Todo")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column())
    canvas.root, draft_input = build_ui(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(560, 480)
    window.show()
    canvas._set_focus(draft_input)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
