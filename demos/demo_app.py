"""Demo 13 · 综合待办：DSL + ForEach / DerivedText。

运行：python demos/demo_app.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import (
    App,
    Box,
    Button,
    Column,
    DerivedText,
    ForEach,
    Row,
    Spacer,
    Text,
    TextInput,
    Theme,
    run,
)

COLORS = ("#ef9a9a", "#90caf9", "#a5d6a7", "#fff59d")


@dataclass
class Task:
    title: str
    done: bool = False
    color: str = "#90caf9"


@run(title="Demo 13 · todo", size=(720, 480), theme=Theme.dark())
class TodoApp(App):
    _busy = False

    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.items = ctx.state(
            [
                Task("学习 MiniUI 布局", color=COLORS[0]),
                Task("跑通 ForEach demo", color=COLORS[1]),
                Task("写一个小应用", color=COLORS[2]),
            ]
        )

    def add_task(self) -> None:
        text = self.ctx.draft.text.strip()
        if not text:
            return
        self.items.value.append(
            Task(text, color=COLORS[len(self.items.value) % len(COLORS)])
        )
        self.items.update()
        self.ctx.draft.text = ""

    def sync_row(self, row, task: Task) -> None:
        bar, label, done_btn, del_btn = row.children
        bar.color = task.color
        prefix = "✓ " if task.done else ""
        title = prefix + task.title
        if label.text != title:
            label.text = title
        done_btn.label = "还原" if task.done else "完成"

    def toggle(self, task: Task) -> None:
        task.done = not task.done
        self.items.update()

    def remove(self, task: Task) -> None:
        if self._busy:
            return
        row = self.ctx.canvas._last_event_node
        while row is not None and not hasattr(row, "paint_dx"):
            row = row.parent
        target = row
        for node in self.ctx.canvas.root.iter_subtree():
            if getattr(node, "_foreach_item", None) is task:
                target = node
                break
        if target is None:
            self.items.value = [t for t in self.items.value if t is not task]
            self.items.update()
            return
        self._busy = True

        def finish() -> None:
            self.items.value = [t for t in self.items.value if t is not task]
            self.items.update()
            target.reset_paint_offset()
            self._busy = False

        self.ctx.animate(target, dx=(0.0, 160.0), duration=300, on_finished=finish)

    def task_row(self, task: Task):
        return Row(
            spacing=8,
            align="stretch",
            nodes=[
                Box(width=6, height=40, color=task.color),
                Text(
                    ("✓ " if task.done else "") + task.title,
                    flex=1,
                    overflow="ellipsis",
                ),
                Button(
                    "还原" if task.done else "完成",
                    min_width=56,
                    on_click=lambda t=task: self.toggle(t),
                ),
                Button("删", min_width=48, on_click=lambda t=task: self.remove(t)),
            ],
        )

    def ui(self) -> None:
        self.root = Row(
            align="stretch",
            nodes=[
                Column(
                    flex=0,
                    padding=16,
                    spacing=10,
                    nodes=[
                        Text("待办", font_size=18, bold=True),
                        DerivedText(
                            lambda: (
                                f"共 {len(self.items.value)} 项 · "
                                f"完成 {sum(1 for t in self.items.value if t.done)} 项"
                            ),
                            deps=[self.items],
                            font_size=13,
                        ),
                        Spacer(flex=1),
                        Button("切换主题", on_click=self.ctx.toggle_theme),
                    ],
                ),
                Column(
                    flex=1,
                    padding=16,
                    spacing=10,
                    nodes=[
                        Text("今日任务", font_size=14, overflow="ellipsis"),
                        Row(
                            spacing=8,
                            align="stretch",
                            nodes=[
                                TextInput(
                                    "",
                                    flex=1,
                                    placeholder="新任务…",
                                    id="draft",
                                    on_submit=self.add_task,
                                ),
                                Button("添加", on_click=self.add_task),
                            ],
                        ),
                        ForEach(
                            self.items,
                            self.task_row,
                            updater=self.sync_row,
                            spacing=8,
                            scroll=True,
                            flex=1,
                        ),
                    ],
                ),
            ],
        )


if __name__ == "__main__":
    TodoApp()
