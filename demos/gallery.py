"""
MiniUI 画廊演示：动态增删卡片 + 滑入滑出动画 + 计数 + 主题。

运行：python demos/gallery.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import (
    Bindings,
    Box,
    Button,
    Column,
    Row,
    ScrollView,
    Spacer,
    State,
    Text,
    Theme,
    UiCanvas,
)

PALETTE = ("#ef9a9a", "#90caf9", "#a5d6a7", "#fff59d", "#ce93d8", "#ffab91")
SLIDE = 140.0


@dataclass
class Card:
    cid: int
    title: str
    color: str
    row: Optional[Row] = field(default=None, repr=False)


def main() -> None:
    app = QApplication(sys.argv)

    cards = State(
        [
            Card(1, "晨曦", PALETTE[0]),
            Card(2, "海面", PALETTE[1]),
            Card(3, "森林", PALETTE[2]),
        ]
    )
    counter = State({"n": 3, "dark": False})
    next_id = [4]

    canvas = UiCanvas(Column(), theme=Theme.light())
    bindings = Bindings(canvas)

    grid = Column(spacing=10, padding=8)
    scroll = ScrollView(grid, flex=1)
    summary = Text("", font_size=14)

    def refresh_summary() -> None:
        summary.set_text(f"共 {len(cards.value)} 张卡片 · 累计创建 {counter.value['n']} 张")

    def build_card(c: Card) -> Row:
        def remove() -> None:
            r = c.row
            if r is None:
                cards.value.remove(c)
                cards.update()
                refresh_summary()
                canvas.repaint_node(summary)
                return

            def done() -> None:
                if c in cards.value:
                    cards.value.remove(c)
                if r is not None:
                    r.reset_paint_offset()
                cards.update()
                refresh_summary()
                canvas.repaint_node(summary)

            canvas.animate_offset(
                r, dx=(r.paint_dx, -SLIDE), duration=260, on_finished=done
            )

        row = Row(
            spacing=12,
            align="center",
            children=[
                Box(width=56, height=56, color=c.color, radius=12, label=str(c.cid)),
                Column(
                    spacing=4,
                    flex=1,
                    children=[
                        Text(c.title, font_size=16, bold=True),
                        Text(c.color, font_size=11),
                    ],
                ),
                Button("删除", on_click=remove, min_width=52, height=32),
            ],
        )
        c.row = row
        return row

    def add_card() -> None:
        i = next_id[0]
        next_id[0] += 1
        c = Card(i, f"卡片 {i}", PALETTE[i % len(PALETTE)])
        cards.value.insert(0, c)
        counter.value["n"] = counter.value["n"] + 1
        counter.update()
        refresh_summary()
        cards.update()

        if c.row is not None:
            c.row.paint_dx = -SLIDE
            canvas.animate_offset(c.row, dx=(-SLIDE, 0.0), duration=320)

    def clear_all() -> None:
        cards.set([])
        cards.update()
        refresh_summary()
        canvas.repaint_node(summary)

    def toggle_theme() -> None:
        counter.value["dark"] = not counter.value["dark"]
        counter.update()
        canvas.set_theme(
            Theme.dark() if counter.value["dark"] else Theme.light()
        )

    canvas.root = Column(
        padding=20,
        spacing=14,
        children=[
            Text("卡片画廊", font_size=22, bold=True),
            Text("添加 / 删除 / 滚动 / 动画 / 换肤", font_size=12),
            summary,
            Row(
                spacing=10,
                children=[
                    Button("＋ 添加卡片", on_click=add_card, min_width=110, height=36),
                    Button("清空", on_click=clear_all, min_width=72, height=36),
                    Spacer(flex=1),
                    Button("深色", on_click=toggle_theme, min_width=72, height=36),
                ],
            ),
            scroll,
        ],
    )

    bindings.list(grid, lambda: cards.value, build_card, cards)

    window = QMainWindow()
    window.setWindowTitle("MiniUI · 画廊")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(480, 560)
    window.show()
    canvas.relayout(force=True)
    refresh_summary()
    canvas.repaint_node(summary)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
