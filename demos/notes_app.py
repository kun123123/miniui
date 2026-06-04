"""Demo 15 · Notes Hub：三栏笔记工作台（搜索 / 筛选 / 编辑 / 动画 / 换肤）。

运行（在 code/ui 目录下）：
    python demos/notes_app.py

验收点：
  - 左栏：视图（全部 / 收藏 / 归档）、标签筛选、统计、换肤
  - 中栏：搜索 + 可滚动笔记列表；选中高亮
  - 右栏：标题 / 正文编辑、保存、★ / 归档 / 删除（滑出动画）
  - 增删改、筛选、搜索均走 State + ForEach / DerivedText
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import QTimer

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
    TextArea,
    TextInput,
    Theme,
    run,
)
from miniui.row import Row as RowNode

TAGS = ("工作", "生活", "学习")
TAG_COLORS = {"工作": "#42a5f5", "生活": "#66bb6a", "学习": "#ab47bc"}
VIEWS = ("all", "starred", "archived")
VIEW_LABELS = {"all": "全部", "starred": "★ 收藏", "archived": "归档"}
SORTS = ("updated", "title")
SORT_LABELS = {"updated": "最近", "title": "标题 A→Z"}


@dataclass
class Note:
    id: int
    title: str
    body: str
    tag: str = "工作"
    starred: bool = False
    archived: bool = False


def _next_id(notes: list[Note]) -> int:
    return max((n.id for n in notes), default=0) + 1


@run(title="Demo 15 · Notes Hub", size=(960, 560), theme=Theme.dark())
class NotesApp(App):
    _title_input: TextInput | None = None
    _body_input: TextInput | None = None
    _view_buttons: dict[str, Button] = {}
    _tag_buttons: dict[str | None, Button] = {}
    _sort_buttons: dict[str, Button] = {}
    _save_btn: Button | None = None

    def mount(self, ctx) -> None:
        super().mount(ctx)
        seed = [
            Note(
                1,
                "MiniUI 布局笔记",
                "measure → layout → paint 三遍 pass；flex 先分槽位再 measure。",
                tag="工作",
                starred=True,
            ),
            Note(
                2,
                "脏标记：layout vs paint",
                "TextInput 改字只 mark_paint_dirty；增删列表才 relayout。",
                tag="学习",
            ),
            Note(
                3,
                "周末采购",
                "牛奶、鸡蛋、这是一段故意写很长的摘要用来演示列表里 ellipsis 截断效果",
                tag="生活",
            ),
            Note(
                4,
                "已归档的旧想法",
                "这条在归档视图里才能看到。",
                tag="工作",
                archived=True,
            ),
        ]
        self.notes = ctx.state(seed)
        self.display = ctx.state(list(seed[:3]))
        self.view = ctx.state("all")
        self.tag_filter = ctx.state(None)
        self.sort = ctx.state("updated")
        self.selected_id = ctx.state(1)

    def _find(self, note_id: int) -> Note | None:
        for n in self.notes.value:
            if n.id == note_id:
                return n
        return None

    def _selected(self) -> Note | None:
        sid = self.selected_id.value
        if sid is None:
            return None
        return self._find(sid)

    def _search_text(self) -> str:
        try:
            return self.ctx.search.text.strip().lower()
        except AttributeError:
            return ""

    def refresh_display(self) -> None:
        q = self._search_text()
        mode = self.view.value
        tag = self.tag_filter.value
        out: list[Note] = []
        for n in self.notes.value:
            if mode == "archived":
                if not n.archived:
                    continue
            elif n.archived:
                continue
            if mode == "starred" and not n.starred:
                continue
            if tag is not None and n.tag != tag:
                continue
            if q and q not in n.title.lower() and q not in n.body.lower():
                continue
            out.append(n)
        if self.sort.value == "title":
            out.sort(key=lambda n: n.title.lower())
        else:
            out.sort(key=lambda n: n.id, reverse=True)
        self.display.set(out)

        sel = self.selected_id.value
        if out and (sel is None or self._find(sel) not in out):
            self.selected_id.set(out[0].id)
        elif not out:
            self.selected_id.set(None)
        self.sync_detail()
        self.sync_filter_buttons()

    def sync_filter_buttons(self) -> None:
        mode = self.view.value
        tag = self.tag_filter.value
        for key, btn in self._view_buttons.items():
            active = key == mode
            label = VIEW_LABELS[key]
            new = f"▸ {label}" if active else f"  {label}"
            if btn.label != new:
                btn.label = new
        for key, btn in self._tag_buttons.items():
            active = key == tag
            name = "全部标签" if key is None else key
            new = f"▸ {name}" if active else f"  {name}"
            if btn.label != new:
                btn.label = new
        sort = self.sort.value
        for key, btn in self._sort_buttons.items():
            active = key == sort
            label = SORT_LABELS[key]
            new = f"▸ {label}" if active else f"  {label}"
            if btn.label != new:
                btn.label = new

    def set_sort(self, mode: str) -> None:
        self.sort.set(mode)
        self.refresh_display()

    def sync_detail(self) -> None:
        if self._title_input is None or self._body_input is None:
            return
        note = self._selected()
        if note is None:
            title, body = "", ""
        else:
            title, body = note.title, note.body
        self._title_input.text = title
        self._body_input.text = body

    def set_view(self, mode: str) -> None:
        self.view.set(mode)
        self.refresh_display()

    def set_tag(self, tag: str | None) -> None:
        self.tag_filter.set(tag)
        self.refresh_display()

    def select_note(self, note: Note) -> None:
        self._persist_detail()
        self.selected_id.set(note.id)
        self.sync_detail()
        self.display.update()

    def _persist_detail(self) -> bool:
        note = self._selected()
        if note is None or self._title_input is None or self._body_input is None:
            return False
        title = self._title_input.text.strip() or "无标题"
        body = self._body_input.text
        if note.title == title and note.body == body:
            return False
        note.title = title
        note.body = body
        return True

    def _flash_saved(self) -> None:
        btn = self._save_btn
        if btn is None:
            return
        btn.label = "已保存 ✓"

        def restore() -> None:
            if btn.label == "已保存 ✓":
                btn.label = "保存"

        QTimer.singleShot(1200, restore)

    def save_detail(self) -> None:
        if self._selected() is None:
            return
        self._persist_detail()
        self.display.update()
        self._flash_saved()

    def create_note(self) -> None:
        if self._persist_detail():
            self.notes.update()
        tag = self.tag_filter.value or TAGS[0]
        nid = _next_id(self.notes.value)
        note = Note(nid, "新笔记", "", tag=tag)
        self.notes.value.append(note)
        self.notes.update()
        self.view.set("all")
        self.selected_id.set(nid)
        self.refresh_display()
        self.sync_detail()

    def toggle_star(self) -> None:
        note = self._selected()
        if note is None:
            return
        note.starred = not note.starred
        self.notes.update()
        self.refresh_display()

    def toggle_archive(self) -> None:
        note = self._selected()
        if note is None:
            return
        note.archived = not note.archived
        if note.archived:
            note.starred = False
        self.notes.update()
        self.refresh_display()

    def delete_note(self) -> None:
        note = self._selected()
        if note is None:
            return

        def remove() -> None:
            if note in self.notes.value:
                self.notes.value.remove(note)
                self.notes.update()
            self.refresh_display()

        self.ctx.animate("editor_card", dx=(0.0, 280.0), duration=260, on_finished=remove)

    def sync_note_row(self, row: RowNode, note: Note) -> None:
        selected = self.selected_id.value == note.id
        stripe: Box = row.children[0]
        col: Column = row.children[1]
        title: Text = col.children[0]
        preview: Text = col.children[1]
        badge: Text = col.children[2]
        stripe.color = "#ffb74d" if selected else TAG_COLORS.get(note.tag, "#78909c")
        title.text = ("★ " if note.starred else "") + note.title
        preview.text = note.body[:48] + ("…" if len(note.body) > 48 else "")
        badge.text = note.tag + (" · 归档" if note.archived else "")

    def note_row(self, note: Note):
        def on_click() -> None:
            self.select_note(note)

        return Row(
            spacing=0,
            align="stretch",
            nodes=[
                Box(width=4, height=56, color=TAG_COLORS.get(note.tag, "#78909c")),
                Column(
                    flex=1,
                    spacing=2,
                    margin=8,
                    nodes=[
                        Text(
                            ("★ " if note.starred else "") + note.title,
                            font_size=14,
                            bold=True,
                            overflow="ellipsis",
                        ),
                        Text(
                            note.body[:48] + ("…" if len(note.body) > 48 else ""),
                            font_size=12,
                            overflow="ellipsis",
                        ),
                        Text(
                            note.tag + (" · 归档" if note.archived else ""),
                            font_size=11,
                        ),
                    ],
                ),
                Button("打开", min_width=52, height=56, on_click=on_click),
            ],
        )

    def ui(self) -> None:
        stats = DerivedText(
            lambda: (
                f"共 {len(self.notes.value)} 条\n"
                f"显示 {len(self.display.value)} 条\n"
                f"★ {sum(1 for n in self.notes.value if n.starred)}"
            ),
            deps=[self.notes, self.display],
            font_size=12,
        )

        view_nodes = []
        for key in VIEWS:
            btn = Button(
                VIEW_LABELS[key],
                min_width=100,
                on_click=lambda k=key: self.set_view(k),
            )
            self._view_buttons[key] = btn
            view_nodes.append(btn)

        tag_nodes = []
        for key in (None, *TAGS):
            name = "全部标签" if key is None else key
            btn = Button(
                name,
                min_width=100,
                on_click=lambda t=key: self.set_tag(t),
            )
            self._tag_buttons[key] = btn
            tag_nodes.append(btn)

        sort_nodes = []
        for key in SORTS:
            btn = Button(
                SORT_LABELS[key],
                min_width=100,
                on_click=lambda k=key: self.set_sort(k),
            )
            self._sort_buttons[key] = btn
            sort_nodes.append(btn)

        self._title_input = TextInput(
            "",
            placeholder="标题…",
            flex=1,
            on_submit=self.save_detail,
        )
        self._body_input = TextArea(
            "",
            placeholder="正文…（Enter 换行，Ctrl+Enter 保存）",
            flex=1,
            min_lines=10,
            on_submit=self.save_detail,
        )

        self._save_btn = Button(
            "保存", min_width=72, on_click=self.save_detail
        )
        editor_card = Column(
            id="editor_card",
            spacing=10,
            align="stretch",
            nodes=[
                Row(
                    spacing=8,
                    align="stretch",
                    nodes=[
                        self._title_input,
                        self._save_btn,
                    ],
                ),
                self._body_input,
                Row(
                    spacing=8,
                    nodes=[
                        Button("★ 收藏", min_width=72, on_click=self.toggle_star),
                        Button("归档", min_width=56, on_click=self.toggle_archive),
                        Spacer(flex=1),
                        Button("删除", min_width=56, on_click=self.delete_note),
                    ],
                ),
                DerivedText(
                    lambda: (
                        "未选中笔记"
                        if self._selected() is None
                        else f"id={self._selected().id} · {self._selected().tag}"
                        + (" · 已归档" if self._selected().archived else "")
                    ),
                    deps=[self.notes, self.selected_id, self.display],
                    font_size=12,
                ),
            ],
        )

        sidebar = Column(
            padding=16,
            spacing=8,
            nodes=[
                Text("MiniNotes", font_size=18, bold=True),
                stats,
                Text("视图", font_size=12),
                *view_nodes,
                Text("标签", font_size=12),
                *tag_nodes,
                Text("排序", font_size=12),
                *sort_nodes,
                Spacer(flex=1),
                Button("切换主题", on_click=self.ctx.toggle_theme),
            ],
        )

        list_panel = Column(
            flex=1,
            padding=16,
            spacing=10,
            align="stretch",
            nodes=[
                Text("笔记列表", font_size=15, bold=True),
                Row(
                    spacing=8,
                    align="stretch",
                    nodes=[
                        TextInput(
                            "",
                            placeholder="搜索标题或正文…",
                            flex=1,
                            id="search",
                            on_submit=self.refresh_display,
                        ),
                        Button("搜", min_width=40, on_click=self.refresh_display),
                        Button("+ 新建", min_width=72, on_click=self.create_note),
                    ],
                ),
                ForEach(
                    self.display,
                    self.note_row,
                    updater=self.sync_note_row,
                    spacing=6,
                    scroll=True,
                    empty="（没有匹配的笔记）",
                ),
            ],
        )

        detail_panel = Column(
            flex=1,
            padding=16,
            spacing=10,
            align="stretch",
            nodes=[
                Text("编辑区", font_size=15, bold=True),
                editor_card,
            ],
        )

        def vrule() -> Box:
            return Box(width=1, color="#333340")

        self.root = Row(
            align="stretch",
            nodes=[
                sidebar,
                vrule(),
                list_panel,
                vrule(),
                detail_panel,
            ],
        )

    def on_ready(self) -> None:
        self.refresh_display()
        for node in self.root.iter_subtree():
            if isinstance(node, Text) and node.overflow == "ellipsis":
                node.warm_display("★ " + node.text)


if __name__ == "__main__":
    NotesApp()
