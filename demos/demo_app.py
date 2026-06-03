"""
MiniUI 综合演示：侧栏 + 筛选 + 搜索 + 滚动列表 + 动画 + 主题 + IME。

运行：python demos/demo_app.py

验证点：布局 flex、ScrollView、State/Bindings、局部重绘、animate_offset、换肤。
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
    TextInput,
    Theme,
    UiCanvas,
)

PRIORITY = {"高": "#e57373", "中": "#ffb74d", "低": "#81c784"}
SLIDE = 120.0


@dataclass
class Task:
    label: str
    category: str
    priority: str
    done: bool = False
    ui_row: Optional[Row] = field(default=None, repr=False)


def main() -> None:
    app = QApplication(sys.argv)

    tasks = State(
        [
            Task("整理 MiniUI 文档", "工作", "高"),
            Task("买周末食材", "生活", "低"),
            Task("复习 flex 两阶段", "学习", "中"),
            Task("综合 demo 验收", "工作", "高"),
            Task("给妈妈打电话", "生活", "中"),
            Task("读 layout 文档", "学习", "低"),
            Task("修复局部重绘", "工作", "中", done=True),
            Task("夜跑 5km", "生活", "低"),
            Task("实现 Theme 换肤", "工作", "中", done=True),
            Task(
                "这是一段特别特别特别特别长的任务标题用来测试省略号",
                "学习",
                "低",
            ),
        ]
    )
    ui = State(
        {
            "filter": "all",
            "category": "全部",
            "add_cat": "工作",
            "title": "全部任务",
            "dark": False,
        }
    )

    canvas = UiCanvas(Column(), theme=Theme.light())
    bindings = Bindings(canvas)

    list_col = Column(spacing=6, padding=4)
    scroll = ScrollView(list_col, flex=1)

    header_title = Text("全部任务", font_size=18, bold=True)
    main_stats = Text("", font_size=12)
    sidebar_stats = Text("", font_size=11)
    cat_hint = Text("将添加到：工作", font_size=11)
    search = TextInput("", placeholder="搜索任务…", flex=1, min_width=80)
    draft = TextInput("", placeholder="新任务，回车添加…", flex=1, min_width=120)

    def visible(t: Task) -> bool:
        u = ui.value
        q = search.text.strip().lower()
        if q and q not in t.label.lower():
            return False
        if u["category"] != "全部" and t.category != u["category"]:
            return False
        if u["filter"] == "pending" and t.done:
            return False
        if u["filter"] == "done" and not t.done:
            return False
        return True

    def filtered_tasks() -> list[Task]:
        return [t for t in tasks.value if visible(t)]

    def refresh_stats() -> None:
        total = len(tasks.value)
        done = sum(1 for t in tasks.value if t.done)
        sidebar_stats.set_text(f"共 {total} 项\n待办 {total - done}")
        main_stats.set_text(f"{total - done} 待办 · {done} 已完成")

    def refresh_view() -> None:
        refresh_stats()
        canvas.relayout()
        canvas.repaint_node(main_stats)
        canvas.repaint_node(sidebar_stats)

    def bounce_row(row: Row) -> None:
        canvas.animate_offset(
            row,
            dy=(0.0, -10.0),
            duration=120,
            on_finished=lambda: canvas.animate_offset(
                row, dy=(-10.0, 0.0), duration=160
            ),
        )

    def set_filter(key: str, title: str) -> None:
        u = dict(ui.value)
        u["filter"] = key
        u["title"] = title
        if key == "all":
            u["category"] = "全部"
            search.text = ""
            search.cursor = 0
        ui.set(u)
        header_title.set_text(title)
        tasks.update()
        canvas.repaint_node(header_title)

    def set_category(cat: str) -> None:
        u = dict(ui.value)
        u["category"] = cat
        ui.set(u)
        tasks.update()

    def pick_add_cat(cat: str) -> None:
        u = dict(ui.value)
        u["add_cat"] = cat
        ui.set(u)
        cat_hint.set_text(f"将添加到：{cat}")
        for ch in category_row.children:
            ch.mark_paint_dirty()
        canvas.repaint_node(category_row)

    def toggle_theme() -> None:
        u = dict(ui.value)
        u["dark"] = not u["dark"]
        ui.set(u)
        canvas.set_theme(Theme.dark() if u["dark"] else Theme.light())

    def build_row(task: Task) -> Row:
        label = task.label
        text = Text(
            ("✓ " if task.done else "") + label,
            font_size=13,
            flex=1,
            overflow="ellipsis",
        )

        def toggle() -> None:
            task.done = not task.done
            text.set_text(("✓ " if task.done else "") + label)
            toggle_btn.label = "●" if task.done else "○"
            toggle_btn.mark_paint_dirty()
            refresh_stats()
            canvas.repaint_node(sidebar_stats)
            canvas.repaint_node(main_stats)
            bounce_row(task.ui_row or row)
            if not visible(task):
                tasks.update()

        def remove() -> None:
            r = task.ui_row or row

            def done() -> None:
                tasks.value.remove(task)
                r.reset_paint_offset()
                tasks.update()

            canvas.animate_offset(
                r, dx=(r.paint_dx, -SLIDE), duration=280, on_finished=done
            )

        toggle_btn = Button(
            "●" if task.done else "○",
            on_click=toggle,
            min_width=30,
            height=28,
        )
        row = Row(
            spacing=8,
            align="center",
            children=[
                Row(
                    spacing=6,
                    align="center",
                    flex=1,
                    children=[
                        Box(
                            width=8,
                            height=8,
                            color=PRIORITY[task.priority],
                            radius=4,
                        ),
                        text,
                    ],
                ),
                Text(f"[{task.category}]", font_size=11),
                toggle_btn,
                Button("×", on_click=remove, min_width=30, height=28),
            ],
        )
        task.ui_row = row
        return row

    def add_task() -> None:
        text = draft.text.strip()
        if not text:
            return
        tasks.value.insert(
            0,
            Task(text, ui.value["add_cat"], "中"),
        )
        draft.text = ""
        draft.cursor = 0
        tasks.update()
        canvas.repaint_node(draft)
        canvas._set_focus(draft)

    draft.on_submit = add_task
    search_btn = Button("搜索", on_click=lambda: tasks.update(), min_width=52)

    category_row = Row(
        spacing=6,
        align="center",
        children=[
            Text("分类:", font_size=12),
            Button("工作", on_click=lambda: pick_add_cat("工作"), min_width=44, height=28),
            Button("生活", on_click=lambda: pick_add_cat("生活"), min_width=44, height=28),
            Button("学习", on_click=lambda: pick_add_cat("学习"), min_width=44, height=28),
            cat_hint,
        ],
    )

    sidebar = Column(
        padding=14,
        spacing=8,
        children=[
            Box(width=96, height=52, label="Mini\nUI"),
            Button("全部", on_click=lambda: set_filter("all", "全部任务"), min_width=96),
            Button("待办", on_click=lambda: set_filter("pending", "待办"), min_width=96),
            Button("已完成", on_click=lambda: set_filter("done", "已完成"), min_width=96),
            Text("侧栏筛选", font_size=11, bold=True),
            Button("全部类", on_click=lambda: set_category("全部"), min_width=96),
            Button("工作", on_click=lambda: set_category("工作"), min_width=96),
            Button("生活", on_click=lambda: set_category("生活"), min_width=96),
            Button("学习", on_click=lambda: set_category("学习"), min_width=96),
            Spacer(flex=1),
            sidebar_stats,
            Button("切换主题", on_click=toggle_theme, min_width=96),
        ],
    )

    main = Column(
        flex=1,
        padding=16,
        spacing=10,
        children=[
            Row(
                spacing=12,
                children=[
                    header_title,
                    Spacer(flex=1),
                    main_stats,
                ],
            ),
            Row(spacing=8, children=[search, search_btn]),
            scroll,
            category_row,
            Row(
                spacing=8,
                children=[
                    draft,
                    Button("添加", on_click=add_task, min_width=64),
                ],
            ),
        ],
    )

    canvas.root = Row(
        spacing=0,
        align="stretch",
        children=[
            sidebar,
            Box(width=1, color="#00000018"),
            main,
        ],
    )

    bindings.list(
        list_col,
        filtered_tasks,
        build_row,
        tasks,
        ui,
        scroll=scroll,
        empty="（没有匹配的任务）",
    )

    window = QMainWindow()
    window.setWindowTitle("MiniUI · 综合演示")
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(760, 520)
    window.show()
    canvas.relayout(force=True)
    refresh_view()
    canvas._set_focus(draft)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
