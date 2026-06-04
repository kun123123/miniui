"""Demo 13 · 综合演示（DSL）：布局、输入、滚动、State、动画与换肤。

运行（在 code/ui 目录下）：
    python demos/demo_app.py

验收点：
  - 侧栏统计 + Spacer + 换肤；主区输入添加、ScrollView 列表
  - State + DerivedText / ForEach 驱动 UI，无需手写 Bindings
  - 长标题 ellipsis；删除时 ctx.animate 滑出后再移除
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
from miniui.row import Row as RowNode

SUBTITLE = (
    "MiniUI 综合 demo：Row / Column / flex / Spacer / ScrollView / "
    "State / ellipsis / animate / set_theme"
)


@dataclass
class Task:
    title: str
    done: bool = False


@run(title="Demo 13 · demo_app", size=(640, 480), theme=Theme.dark())
class TodoApp(App):
    _stats: Text | None = None

    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.items = ctx.state([
            Task("验收 miniui demos"),
            Task("写一篇超长标题用来演示 Text 的 overflow ellipsis 在窄窗口下的效果"),
            Task("整理 README"),
        ])

    def add_task(self) -> None:
        title = self.ctx.draft.text.strip()
        if not title:
            return
        self.ctx.draft.text = ""
        self.items.value.append(Task(title))
        self.items.update()

    def toggle_theme(self) -> None:
        self.ctx.toggle_theme()

    def sync_stats(self) -> None:
        if self._stats is None:
            return
        text = (
            f"共 {len(self.items.value)} 项\n"
            f"待办 {sum(1 for t in self.items.value if not t.done)}"
        )
        if self._stats._text == text:
            return
        self._stats._text = text
        self._stats._display_key = None
        self._stats.mark_paint_dirty()

    def sync_task_row(self, row: Row, task: Task) -> None:
        row.children[0].color = "#66bb6a" if task.done else "#42a5f5"
        title: Text = row.children[1]
        label = f"✓ {task.title}" if task.done else task.title
        if title._text != label:
            title._text = label
            title._display_key = None
            title.mark_paint_dirty()
        row.children[2].label = "撤销" if task.done else "完成"

    def on_ready(self) -> None:
        """预热完成态 ellipsis，避免首次点「完成」在 paint 里算长串。"""
        for node in self.root.iter_subtree():
            if not isinstance(node, RowNode) or not node.children:
                continue
            title_node = node.children[1]
            if not isinstance(title_node, Text) or title_node.overflow != "ellipsis":
                continue
            title_node.warm_display(f"✓ {title_node.text}")

    def task_row(self, task: Task):
        ctx = self.ctx
        stripe = "#66bb6a" if task.done else "#42a5f5"
        label = f"✓ {task.title}" if task.done else task.title

        def toggle_done() -> None:
            task.done = not task.done
            self.sync_task_row(row, task)
            self.sync_stats()

        def remove() -> None:
            def done() -> None:
                if task in self.items.value:
                    self.items.value.remove(task)
                    self.items.update()

            ctx.animate("row", dx=(0.0, 160.0), duration=280, on_finished=done)

        row = Row(
            spacing=8,
            align="center",
            id="row",
            nodes=[
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

    def ui(self) -> None:
        stats = DerivedText(
            lambda: f"共 {len(self.items.value)} 项\n"
            f"待办 {sum(1 for t in self.items.value if not t.done)}",
            deps=[self.items],
            font_size=12,
        )
        self._stats = stats
        self.root = Row(
            align="stretch",
            nodes=[
                Column(
                    padding=16,
                    spacing=10,
                    nodes=[
                        Text("待办", font_size=18, bold=True),
                        stats,
                        Spacer(flex=1),
                        Button("切换主题", on_click=self.toggle_theme),
                    ],
                ),
                Column(
                    flex=1,
                    padding=16,
                    spacing=12,
                    align="stretch",
                    nodes=[
                        Text(SUBTITLE, font_size=13, overflow="ellipsis"),
                        Row(
                            spacing=8,
                            align="stretch",
                            nodes=[
                                TextInput(
                                    "",
                                    placeholder="新任务，回车添加…",
                                    flex=1,
                                    id="draft",
                                    on_submit=self.add_task,
                                ),
                                Button("添加", on_click=self.add_task, min_width=64),
                            ],
                        ),
                        ForEach(
                            self.items,
                            self.task_row,
                            updater=self.sync_task_row,
                            spacing=8,
                            scroll=True,
                        ),
                    ],
                ),
            ],
        )


if __name__ == "__main__":
    TodoApp()
