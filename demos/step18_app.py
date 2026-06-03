"""
Step 18：TaskHub —— MiniUI 综合应用。

运行：python demos/step18_app.py

侧栏导航 + 分类筛选 + 搜索 + 滚动任务列表 + 优先级 + 主题 + IME 输入。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Box, Button, Column, Row, ScrollView, Spacer, Text, TextInput, Theme, UiCanvas

PRIORITY_COLORS = {"高": "#e57373", "中": "#ffb74d", "低": "#81c784"}


def build_app(canvas: UiCanvas) -> TextInput:
    state = {
        "filter": "all",
        "category": "全部",
        "dark": False,
        "add_category": "工作",
    }
    items: list[dict] = []
    list_col = Column(spacing=6, padding=4)
    scroll = ScrollView(list_col, flex=1)
    header_title = Text("全部任务", font_size=18, bold=True)
    sidebar_stats = Text("", font_size=11)
    main_stats = Text("", font_size=12)
    cat_hint = Text("将添加到：工作", font_size=11)
    search = TextInput("", placeholder="搜索任务…", flex=1, min_width=100)
    draft = TextInput("", placeholder="新任务，回车添加…", flex=1, min_width=140)

    def refresh_stats() -> None:
        total = len(items)
        done = sum(1 for it in items if it["done"])
        sidebar_stats.set_text(f"共 {total} 项\n待办 {total - done}")
        main_stats.set_text(f"{total - done} 待办 · {done} 已完成")
        canvas.repaint_node(sidebar_stats)
        canvas.repaint_node(main_stats)

    def visible(item: dict) -> bool:
        q = search.text.strip().lower()
        if q and q not in item["label"].lower():
            return False
        if state["category"] != "全部" and item["category"] != state["category"]:
            return False
        if state["filter"] == "pending" and item["done"]:
            return False
        if state["filter"] == "done" and not item["done"]:
            return False
        return True

    def refresh_list() -> None:
        for child in list(list_col.children):
            list_col.remove_child(child)
        any_row = False
        for item in items:
            if visible(item):
                list_col.add_child(item["row"])
                any_row = True
        if not any_row:
            list_col.add_child(Text("（没有匹配的任务）", font_size=13))
        scroll.scroll_y = 0.0
        scroll._clamp_scroll()
        scroll.mark_paint_dirty()
        for node in scroll.child.iter_subtree():
            node.mark_paint_dirty()
        canvas.relayout()
        canvas.repaint()
        refresh_stats()

    def set_filter(key: str, title: str) -> None:
        state["filter"] = key
        if key == "all":
            state["category"] = "全部"
            search.text = ""
            search.cursor = 0
        header_title.set_text(title)
        refresh_list()
        canvas.repaint_node(header_title)

    def set_category(cat: str) -> None:
        state["category"] = cat
        refresh_list()

    def pick_category(cat: str) -> None:
        state["add_category"] = cat
        cat_hint.set_text(f"将添加到：{cat}")
        canvas.repaint_node(cat_hint)

    def toggle_theme() -> None:
        state["dark"] = not state["dark"]
        canvas.set_theme(Theme.dark() if state["dark"] else Theme.light())

    def make_task(
        label: str,
        category: str,
        priority: str,
        *,
        done: bool = False,
    ) -> dict:
        text = Text(
            ("✓ " if done else "") + label,
            font_size=13,
            flex=1,
            overflow="ellipsis",
        )
        item: dict = {
            "done": done,
            "label": label,
            "category": category,
            "priority": priority,
        }

        def toggle() -> None:
            item["done"] = not item["done"]
            text.set_text(("✓ " if item["done"] else "") + label)
            canvas.relayout()
            canvas.repaint()
            refresh_stats()
            if not visible(item):
                refresh_list()

        def remove() -> None:
            if item.get("row") in list_col.children:
                list_col.remove_child(item["row"])
            items[:] = [it for it in items if it is not item]
            canvas.relayout()
            canvas.repaint()
            refresh_stats()

        item["row"] = Row(
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
                            color=PRIORITY_COLORS[priority],
                            radius=4,
                        ),
                        text,
                    ],
                ),
                Text(f"[{category}]", font_size=11),
                Button(
                    "●" if done else "○",
                    on_click=toggle,
                    min_width=30,
                    height=28,
                ),
                Button("×", on_click=remove, min_width=30, height=28),
            ],
        )
        return item

    def add_task() -> None:
        label = draft.text.strip()
        if not label:
            return
        items.insert(0, make_task(label, state["add_category"], "中"))
        draft.text = ""
        draft.cursor = 0
        refresh_list()
        scroll.scroll_by(1e9)
        canvas._set_focus(draft)

    draft.on_submit = add_task

    for seed in (
        ("整理 MiniUI 博客大纲", "工作", "高"),
        ("买周末食材", "生活", "低"),
        ("复习 flex measure 两阶段", "学习", "中"),
        ("TaskHub 综合 demo 验收", "工作", "高"),
        ("给妈妈打电话", "生活", "中"),
        ("读 Flutter layout 文档", "学习", "低"),
        ("修复 Todo 勾选 relayout", "工作", "中", True),
        ("夜跑 5km", "生活", "低"),
        ("实现 Theme 换肤", "工作", "中", True),
        ("这是一段特别特别特别特别特别长的任务标题用来测试省略号", "学习", "低"),
    ):
        done = seed[3] if len(seed) > 3 else False
        items.append(make_task(seed[0], seed[1], seed[2], done=done))

    sidebar = Column(
        padding=14,
        spacing=8,
        children=[
            Box(width=96, height=52, label="Task\nHub"),
            Button("全部", on_click=lambda: set_filter("all", "全部任务"), min_width=96),
            Button("待办", on_click=lambda: set_filter("pending", "待办事项"), min_width=96),
            Button("已完成", on_click=lambda: set_filter("done", "已完成"), min_width=96),
            Text("分类", font_size=11, bold=True),
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
            Row(
                spacing=8,
                children=[
                    search,
                    Button("搜索", on_click=refresh_list, min_width=56),
                ],
            ),
            scroll,
            Row(
                spacing=6,
                align="center",
                children=[
                    Text("分类:", font_size=12),
                    Button("工作", on_click=lambda: pick_category("工作"), min_width=44, height=28),
                    Button("生活", on_click=lambda: pick_category("生活"), min_width=44, height=28),
                    Button("学习", on_click=lambda: pick_category("学习"), min_width=44, height=28),
                    cat_hint,
                ],
            ),
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

    refresh_list()
    return draft


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("TaskHub · MiniUI")
    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)
    canvas = UiCanvas(Column(), theme=Theme.light())
    draft = build_app(canvas)
    layout.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(720, 520)
    window.show()
    canvas.relayout(force=True)
    canvas._set_focus(draft)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
