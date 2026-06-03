"""Demo 13 · 综合演示：整合布局、输入、滚动、State、动画与换肤。

运行（在 code/ui 目录下）：
    python demos/demo_app.py

验收点：
  - 侧栏统计 + Spacer + 换肤；主区输入添加、ScrollView 列表
  - State + Bindings 驱动列表与统计，无需手写 refresh
  - 长标题 ellipsis；删除时 animate_offset 滑出后再移除
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

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
    TextInput,
    Theme,
    UiCanvas,
)

SUBTITLE = (
    "MiniUI 综合 demo：Row / Column / flex / Spacer / ScrollView / "
    "State / Bindings / ellipsis / animate_offset / set_theme"
)


@dataclass
class Task:
    title: str
    done: bool = False


def main() -> None:
    app = QApplication(sys.argv)

    items = State(
        [
            Task("验收 miniui demos"),
            Task("写一篇超长标题用来演示 Text 的 overflow ellipsis 在窄窗口下的效果"),
            Task("整理 README"),
        ]
    )
    list_col = Column(spacing=8, align="stretch")
    sidebar_stats = Text("", font_size=12)
    is_dark = [True]
    draft = TextInput("", placeholder="新任务，回车添加…", flex=1)

    def stats_text() -> str:
        total = len(items.value)
        pending = sum(1 for t in items.value if not t.done)
        return f"共 {total} 项\n待办 {pending}"

    def add_task() -> None:
        title = draft.text.strip()
        if not title:
            return
        items.value.append(Task(title))
        items.update()
        draft.text = ""

    draft.on_submit = add_task

    def toggle_theme() -> None:
        is_dark[0] = not is_dark[0]
        canvas.set_theme(Theme.dark() if is_dark[0] else Theme.light())

    scroll = ScrollView(flex=1, child=list_col)

    canvas = UiCanvas(
        theme=Theme.dark(),
        root=Row(
            align="stretch",
            children=[
                Column(
                    padding=16,
                    spacing=10,
                    children=[
                        Text("待办", font_size=18, bold=True),
                        sidebar_stats,
                        Spacer(flex=1),
                        Button("切换主题", on_click=toggle_theme),
                    ],
                ),
                Column(
                    flex=1,
                    padding=16,
                    spacing=12,
                    align="stretch",
                    children=[
                        Text(SUBTITLE, font_size=13, overflow="ellipsis"),
                        Row(
                            spacing=8,
                            align="stretch",
                            children=[
                                draft,
                                Button("添加", on_click=add_task, min_width=64),
                            ],
                        ),
                        scroll,
                    ],
                ),
            ],
        ),
    )

    def build_task_row(task: Task) -> Row:
        stripe = "#66bb6a" if task.done else "#42a5f5"
        label = f"✓ {task.title}" if task.done else task.title

        def toggle_done() -> None:
            task.done = not task.done
            items.update()

        def remove() -> None:
            def done() -> None:
                if task in items.value:
                    items.value.remove(task)
                    items.update()

            canvas.animate_offset(row, dx=(0.0, 160.0), duration=280, on_finished=done)

        row = Row(
            spacing=8,
            align="center",
            children=[
                Box(width=6, height=36, color=stripe),
                Text(label, flex=1, overflow="ellipsis"),
                Button(
                    "撤销" if task.done else "完成",
                    min_width=56,
                    on_click=toggle_done,
                ),
                Button("删", min_width=40, on_click=remove),
            ],
        )
        return row

    bindings = Bindings(canvas)
    bindings.text(sidebar_stats, stats_text, items)
    bindings.list(
        list_col,
        lambda: items.value,
        build_task_row,
        items,
        scroll=scroll,
    )

    window = QMainWindow()
    window.setWindowTitle("Demo 13 · demo_app")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(640, 480)
    window.show()
    canvas.relayout(force=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
