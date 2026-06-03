"""State + Bindings + with 块：响应式列表。"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Bindings, Button, Column, Row, ScrollView, State, Text, TextInput, UiCanvas


@dataclass
class Item:
    label: str
    ui_row: Optional[Row] = field(default=None, repr=False)


def main() -> None:
    app = QApplication(sys.argv)
    items = State([Item("买牛奶"), Item("写文档")])
    canvas = UiCanvas(Column())
    bindings = Bindings(canvas)

    list_col = Column(spacing=6, padding=4)
    scroll = ScrollView(list_col, flex=1)
    draft = TextInput("", placeholder="新任务，回车添加", flex=1)

    def build_row(item: Item) -> Row:
        row = Row(spacing=8, align="center")
        with row:
            Text(item.label, font_size=13, flex=1)

            def remove() -> None:
                items.value.remove(item)
                items.update()

            Button("×", on_click=remove, min_width=28, height=28)
        item.ui_row = row
        return row

    def add() -> None:
        text = draft.text.strip()
        if not text:
            return
        items.value.insert(0, Item(text))
        draft.text = ""
        draft.cursor = 0
        items.update()
        canvas.repaint_node(draft)

    draft.on_submit = add

    # with 只自动挂载「块内新创建的节点」；scroll/draft 等已有对象要用 children=
    canvas.root = Column(
        padding=16,
        spacing=10,
        children=[
            Text("State 列表示例", font_size=16, bold=True),
            scroll,
            Row(
                spacing=8,
                children=[
                    draft,
                    Button("添加", on_click=add, min_width=56),
                ],
            ),
        ],
    )
    bindings.list(list_col, lambda: items.value, build_row, items, scroll=scroll)

    window = QMainWindow()
    window.setWindowTitle("state_with")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(400, 360)
    window.show()
    canvas.relayout(force=True)
    canvas._set_focus(draft)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
