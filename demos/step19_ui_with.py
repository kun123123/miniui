"""
Step 19：with 块 + State 响应式 UI。

运行：python demos/step19_ui_with.py

静态布局用 ``with Column():``，数据用 ``State`` + ``Bindings``，
改 filter / items 时列表与统计文字自动刷新；全程不混用 ``children=[...]``。
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

PRIORITY_COLORS = {"高": "#e57373", "中": "#ffb74d", "低": "#81c784"}


@dataclass
class TaskItem:
    label: str
    category: str
    priority: str
    done: bool = False


def build_task_row(item: TaskItem, items: State[list[TaskItem]]) -> Row:
    def toggle() -> None:
        item.done = not item.done
        items.update()

    def remove() -> None:
        items.value.remove(item)
        items.update()

    row = Row(spacing=8, align="center")
    with row:
        with Row(spacing=6, align="center", flex=1):
            Box(
                width=8,
                height=8,
                color=PRIORITY_COLORS[item.priority],
                radius=4,
            )
            Text(
                ("✓ " if item.done else "") + item.label,
                font_size=13,
                flex=1,
                overflow="ellipsis",
            )
        Text(f"[{item.category}]", font_size=11)
        Button(
            "●" if item.done else "○",
            on_click=toggle,
            min_width=30,
            height=28,
        )
        Button("×", on_click=remove, min_width=30, height=28)
    return row


def seed_items() -> list[TaskItem]:
    rows = (
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
    )
    out: list[TaskItem] = []
    for seed in rows:
        done = seed[3] if len(seed) > 3 else False
        out.append(TaskItem(seed[0], seed[1], seed[2], done=done))
    return out


def build_app(canvas: UiCanvas) -> TextInput:
    items = State(seed_items())
    filter_key = State("all")
    list_category = State("全部")
    page_title = State("全部任务")
    add_category = State("工作")
    search_query = State("")
    dark = State(False)

    search: TextInput | None = None
    draft: TextInput | None = None
    list_col: Column | None = None
    scroll: ScrollView | None = None
    header_title: Text | None = None
    sidebar_stats: Text | None = None
    main_stats: Text | None = None
    cat_hint: Text | None = None

    def item_visible(item: TaskItem) -> bool:
        q = search_query.value.strip().lower()
        if q and q not in item.label.lower():
            return False
        if list_category.value != "全部" and item.category != list_category.value:
            return False
        if filter_key.value == "pending" and item.done:
            return False
        if filter_key.value == "done" and not item.done:
            return False
        return True

    def visible_items() -> list[TaskItem]:
        return [it for it in items.value if item_visible(it)]

    def set_filter(key: str, title: str) -> None:
        filter_key.set(key)
        page_title.set(title)
        if key == "all":
            list_category.set("全部")
            assert search is not None
            search.text = ""
            search.cursor = 0
            search_query.set("")

    def set_category(cat: str) -> None:
        list_category.set(cat)

    def pick_category(cat: str) -> None:
        add_category.set(cat)

    def toggle_theme() -> None:
        dark.set(not dark.value)
        canvas.set_theme(Theme.dark() if dark.value else Theme.light())

    def add_task() -> None:
        assert draft is not None
        label = draft.text.strip()
        if not label:
            return
        items.value.insert(0, TaskItem(label, add_category.value, "中"))
        items.update()
        draft.text = ""
        draft.cursor = 0
        canvas._set_focus(draft)

    root = Row(spacing=0, align="stretch")
    with root:
        with Column(padding=14, spacing=8):
            Box(width=96, height=52, label="Task\nHub")
            Button("全部", on_click=lambda: set_filter("all", "全部任务"), min_width=96)
            Button("待办", on_click=lambda: set_filter("pending", "待办事项"), min_width=96)
            Button("已完成", on_click=lambda: set_filter("done", "已完成"), min_width=96)
            Text("分类", font_size=11, bold=True)
            Button("全部类", on_click=lambda: set_category("全部"), min_width=96)
            Button("工作", on_click=lambda: set_category("工作"), min_width=96)
            Button("生活", on_click=lambda: set_category("生活"), min_width=96)
            Button("学习", on_click=lambda: set_category("学习"), min_width=96)
            Spacer(flex=1)
            sidebar_stats = Text("", font_size=11)
            Button("切换主题", on_click=toggle_theme, min_width=96)

        Box(width=1, color="#00000018")

        with Column(flex=1, padding=16, spacing=10):
            with Row(spacing=12):
                header_title = Text("", font_size=18, bold=True)
                Spacer(flex=1)
                main_stats = Text("", font_size=12)

            with Row(spacing=8):
                search = TextInput("", placeholder="搜索任务…", flex=1, min_width=100)
                Button(
                    "搜索",
                    on_click=lambda: search_query.set(search.text.strip()),
                    min_width=56,
                )

            with ScrollView(flex=1) as scroll:
                list_col = Column(spacing=6, padding=4)

            with Row(spacing=6, align="center"):
                Text("分类:", font_size=12)
                Button("工作", on_click=lambda: pick_category("工作"), min_width=44, height=28)
                Button("生活", on_click=lambda: pick_category("生活"), min_width=44, height=28)
                Button("学习", on_click=lambda: pick_category("学习"), min_width=44, height=28)
                cat_hint = Text("", font_size=11)

            with Row(spacing=8):
                draft = TextInput("", placeholder="新任务，回车添加…", flex=1, min_width=140)
                Button("添加", on_click=add_task, min_width=64)

    canvas.root = root
    assert (
        draft is not None
        and search is not None
        and list_col is not None
        and scroll is not None
        and header_title is not None
        and sidebar_stats is not None
        and main_stats is not None
        and cat_hint is not None
    )
    draft.on_submit = add_task

    bindings = Bindings(canvas)

    def sidebar_text() -> str:
        total = len(items.value)
        done = sum(1 for it in items.value if it.done)
        return f"共 {total} 项\n待办 {total - done}"

    def main_text() -> str:
        total = len(items.value)
        done = sum(1 for it in items.value if it.done)
        return f"{total - done} 待办 · {done} 已完成"

    bindings.text(sidebar_stats, sidebar_text, items)
    bindings.text(main_stats, main_text, items)
    bindings.text(header_title, lambda: page_title.value, page_title)
    bindings.text(cat_hint, lambda: f"将添加到：{add_category.value}", add_category)
    bindings.list(
        list_col,
        visible_items,
        lambda item: build_task_row(item, items),
        items,
        filter_key,
        list_category,
        search_query,
        scroll=scroll,
    )

    return draft


def main() -> None:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("TaskHub · with + State · MiniUI")
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
