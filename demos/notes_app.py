"""MiniNotes · 三栏笔记工作台（MiniUI 旗舰示例）。

运行（在 code/ui 目录下）：
    python demos/notes_app.py

能力串联：
  - 三栏 flex 布局 · 搜索 / 视图 / 标签 / 排序
  - ForEach + updater（选中、★ paint-only）
  - TextInput + TextArea · 本地 JSON 持久化
  - 删除滑出动画 · 暗色/亮色换肤 · 封面 Image
"""

from __future__ import annotations

import datetime
import json
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
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
    Image,
    Row,
    Spacer,
    Text,
    TextArea,
    TextInput,
    Theme,
    run,
)

_DATA = Path(__file__).resolve().parent / "data" / "notes.json"
_COVER = Path(__file__).resolve().parent / "assets" / "image.png"

TAGS = ("工作", "生活", "学习")
TAG_COLORS = {"工作": "#42a5f5", "生活": "#66bb6a", "学习": "#ab47bc"}
VIEWS = ("all", "starred", "archived")
VIEW_LABELS = {"all": "全部", "starred": "★ 收藏", "archived": "归档"}
SORTS = ("updated", "title")
SORT_LABELS = {"updated": "最近", "title": "标题 A→Z"}


@dataclass
class Note:
    id: str
    title: str
    body: str
    tag: str
    starred: bool = False
    archived: bool = False
    updated: float = field(default_factory=time.time)


def _seed_notes() -> list[Note]:
    now = time.time()
    return [
        Note(
            str(uuid.uuid4()),
            "欢迎使用 MiniNotes",
            "这是 MiniUI 旗舰示例。\n\n左侧筛选，中间列表，右侧编辑。\nCtrl+Enter 可快速保存正文。",
            "学习",
            starred=True,
            updated=now,
        ),
        Note(
            str(uuid.uuid4()),
            "购物清单",
            "牛奶\n鸡蛋\n面包",
            "生活",
            updated=now - 3600,
        ),
        Note(
            str(uuid.uuid4()),
            "周报要点",
            "1. ScrollView 局部重绘\n2. TextArea 软换行\n3. Image fit 模式",
            "工作",
            updated=now - 7200,
        ),
    ]


def _load_notes() -> list[Note]:
    if not _DATA.is_file():
        return _seed_notes()
    try:
        raw = json.loads(_DATA.read_text(encoding="utf-8"))
        return [Note(**item) for item in raw]
    except (json.JSONDecodeError, TypeError, KeyError):
        return _seed_notes()


def _save_notes(notes: list[Note]) -> None:
    _DATA.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(n) for n in notes]
    _DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


@run(title="MiniNotes", size=(1080, 640), theme=Theme.dark())
class NotesApp(App):
    _view_buttons: dict[str, Button] = {}
    _tag_buttons: dict[str | None, Button] = {}
    _sort_buttons: dict[str, Button] = {}
    _title_input: TextInput | None = None
    _body_input: TextArea | None = None
    _save_btn: Button | None = None
    _star_btn: Button | None = None
    _busy = False

    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.notes = ctx.state(_load_notes())
        self.display = ctx.state(list(self.notes.value))
        self.view = ctx.state("all")
        self.tag_filter = ctx.state(None)
        self.sort = ctx.state("updated")
        self.selected_id = ctx.state(
            self.notes.value[0].id if self.notes.value else ""
        )
        self.search = ctx.state("")

        def on_select() -> None:
            self.sync_detail()
            self.display.update()
            self._sync_star_button()

        self.selected_id.subscribe(on_select)

    def refresh_display(self) -> None:
        q = self.search.value.strip().lower()
        view = self.view.value
        tag = self.tag_filter.value
        out: list[Note] = []
        for note in self.notes.value:
            if view == "starred" and not note.starred:
                continue
            if view == "archived" and not note.archived:
                continue
            if view == "all" and note.archived:
                continue
            if tag is not None and note.tag != tag:
                continue
            if q and q not in note.title.lower() and q not in note.body.lower():
                continue
            out.append(note)
        if self.sort.value == "title":
            out.sort(key=lambda n: n.title.lower())
        else:
            out.sort(key=lambda n: n.updated, reverse=True)
        if self.display.value == out:
            self.display.update()
        else:
            self.display.set(out)

    def _selected(self) -> Note | None:
        sid = self.selected_id.value
        for note in self.notes.value:
            if note.id == sid:
                return note
        return None

    def _persist_detail(self) -> bool:
        if self._title_input is None or self._body_input is None:
            return False
        note = self._selected()
        if note is None:
            return False
        title = self._title_input.text.strip()
        body = self._body_input.text
        if note.title == title and note.body == body:
            return False
        note.title = title or "（无标题）"
        note.body = body
        note.updated = time.time()
        _save_notes(self.notes.value)
        return True

    def sync_detail(self) -> None:
        if self._title_input is None or self._body_input is None:
            return
        note = self._selected()
        if note is None:
            title, body = "", ""
        else:
            title, body = note.title, note.body
        if self._title_input.text != title:
            self._title_input.text = title
        if self._body_input.text != body:
            self._body_input.text = body

    def save_detail(self) -> None:
        if self._persist_detail():
            self.notes.update()
            self.refresh_display()
        if self._save_btn is not None:
            self._save_btn.label = "已保存"
            self._save_btn.mark_paint_dirty()

            def reset() -> None:
                if self._save_btn is not None:
                    self._save_btn.label = "保存"
                    self._save_btn.mark_paint_dirty()

            QTimer.singleShot(900, reset)

    def select_note(self, note: Note) -> None:
        if self._persist_detail():
            self.notes.update()
            self.refresh_display()
        self.selected_id.set(note.id)

    def set_view(self, mode: str) -> None:
        self.view.set(mode)
        self.refresh_display()
        self._sync_nav_buttons()

    def set_tag(self, tag: str | None) -> None:
        self.tag_filter.set(tag)
        self.refresh_display()
        self._sync_nav_buttons()

    def set_sort(self, mode: str) -> None:
        self.sort.set(mode)
        self.refresh_display()
        self._sync_nav_buttons()

    def run_search(self) -> None:
        self.search.set(self.ctx.search.text)
        self.refresh_display()

    def star_selected(self) -> None:
        note = self._selected()
        if note is not None:
            self.toggle_star(note)

    def create_note(self) -> None:
        if self._persist_detail():
            self.notes.update()
        tag = self.tag_filter.value or TAGS[0]
        note = Note(str(uuid.uuid4()), "新笔记", "", tag)
        self.notes.value.insert(0, note)
        self.notes.update()
        self.selected_id.set(note.id)
        self.refresh_display()
        self.sync_detail()
        _save_notes(self.notes.value)
        if self._title_input is not None:
            self.ctx.canvas._set_focus(self._title_input)

    def toggle_star(self, note: Note) -> None:
        note.starred = not note.starred
        note.updated = time.time()
        _save_notes(self.notes.value)
        self.notes.update()
        self.refresh_display()
        self._sync_star_button()

    def _sync_star_button(self) -> None:
        note = self._selected()
        if self._star_btn is None:
            return
        label = "★ 已收藏" if note and note.starred else "☆ 收藏"
        if self._star_btn.label != label:
            self._star_btn.label = label

    def toggle_archive(self) -> None:
        note = self._selected()
        if note is None:
            return
        note.archived = not note.archived
        note.updated = time.time()
        self.notes.update()
        self.refresh_display()
        _save_notes(self.notes.value)

    def delete_note(self) -> None:
        if self._busy:
            return
        note = self._selected()
        if note is None:
            return
        self._busy = True
        card = self.ctx.editor_card

        def finish() -> None:
            self.notes.value = [n for n in self.notes.value if n.id != note.id]
            self.notes.update()
            if self.notes.value:
                self.selected_id.set(self.notes.value[0].id)
            else:
                self.selected_id.set("")
            self.refresh_display()
            self.sync_detail()
            card.reset_paint_offset()
            _save_notes(self.notes.value)
            self._busy = False

        self.ctx.animate("editor_card", dx=(0.0, 220.0), duration=320, on_finished=finish)

    def _sync_nav_buttons(self) -> None:
        for key, btn in self._view_buttons.items():
            mark = "● " if self.view.value == key else ""
            btn.label = mark + VIEW_LABELS[key]
        for key, btn in self._tag_buttons.items():
            label = "全部标签" if key is None else key
            mark = "● " if self.tag_filter.value == key else ""
            btn.label = mark + label
        for key, btn in self._sort_buttons.items():
            mark = "● " if self.sort.value == key else ""
            btn.label = mark + SORT_LABELS[key]

    def sync_note_row(self, row, note: Note) -> None:
        selected = self.selected_id.value == note.id
        tag_box, title_btn, star_btn = row.children[0], row.children[1], row.children[2]
        tag_box.color = TAG_COLORS.get(note.tag, "#888888")
        prefix = "▸ " if selected else ""
        title = prefix + (note.title or "（无标题）")
        if title_btn.label != title:
            title_btn.label = title
        star = "★" if note.starred else "☆"
        if star_btn.label != star:
            star_btn.label = star

    def note_row(self, note: Note):
        return Row(
            spacing=6,
            align="stretch",
            nodes=[
                Box(width=4, height=46, color=TAG_COLORS.get(note.tag, "#888")),
                Button(
                    (note.title or "（无标题）"),
                    flex=1,
                    min_width=100,
                    height=46,
                    on_click=lambda n=note: self.select_note(n),
                ),
                Button(
                    "★" if note.starred else "☆",
                    min_width=40,
                    height=32,
                    on_click=lambda n=note: self.toggle_star(n),
                ),
            ],
        )

    def on_ready(self) -> None:
        self.refresh_display()
        self.sync_detail()
        self._sync_nav_buttons()
        self._sync_star_button()

    def ui(self) -> None:
        view_nodes = []
        for key in VIEWS:
            btn = Button(
                VIEW_LABELS[key],
                min_width=108,
                on_click=lambda k=key: self.set_view(k),
            )
            self._view_buttons[key] = btn
            view_nodes.append(btn)

        tag_nodes = []
        for key in (None, *TAGS):
            label = "全部标签" if key is None else key
            btn = Button(
                label,
                min_width=108,
                on_click=lambda t=key: self.set_tag(t),
            )
            self._tag_buttons[key] = btn
            tag_nodes.append(btn)

        sort_nodes = []
        for key in SORTS:
            btn = Button(
                SORT_LABELS[key],
                min_width=108,
                on_click=lambda k=key: self.set_sort(k),
            )
            self._sort_buttons[key] = btn
            sort_nodes.append(btn)

        self._title_input = TextInput("", flex=1, id="title", placeholder="标题")
        self._body_input = TextArea(
            "",
            flex=1,
            min_lines=6,
            placeholder="正文… Enter 换行，Ctrl+Enter 保存",
            id="body",
            on_submit=self.save_detail,
        )
        self._save_btn = Button("保存", min_width=72, on_click=self.save_detail)
        self._star_btn = Button("☆ 收藏", min_width=72, on_click=self.star_selected)

        cover_image: Image | None = None
        if _COVER.is_file():
            cover_image = Image(str(_COVER), width=200, height=120, fit="cover")

        sidebar_nodes = [
            Text("MiniNotes", font_size=18, bold=True),
            Text("视图", font_size=12),
            *view_nodes,
            Text("标签", font_size=12),
            *tag_nodes,
            Text("排序", font_size=12),
            *sort_nodes,
            Spacer(flex=1),
            DerivedText(
                lambda: (
                    f"共 {len(self.notes.value)} 篇 · "
                    f"显示 {len(self.display.value)} 篇"
                ),
                deps=[self.notes, self.display],
                font_size=12,
            ),
            Button("＋ 新笔记", on_click=self.create_note),
            Button("切换主题", on_click=self.ctx.toggle_theme),
        ]

        editor_header: list = []
        if cover_image is not None:
            editor_header.append(
                Row(
                    spacing=10,
                    align="stretch",
                    nodes=[
                        cover_image,
                        Column(
                            flex=1,
                            spacing=4,
                            nodes=[
                                DerivedText(
                                    lambda: self._editor_meta(),
                                    deps=[self.selected_id, self.notes],
                                    font_size=12,
                                ),
                            ],
                        ),
                    ],
                )
            )
        else:
            editor_header.append(
                DerivedText(
                    lambda: self._editor_meta(),
                    deps=[self.selected_id, self.notes],
                    font_size=12,
                )
            )

        editor_card = Column(
            id="editor_card",
            flex=1,
            spacing=10,
            align="stretch",
            nodes=[
                *editor_header,
                Row(
                    spacing=8,
                    align="stretch",
                    nodes=[self._title_input, self._save_btn],
                ),
                self._body_input,
                Row(
                    spacing=8,
                    nodes=[
                        self._star_btn,
                        Button("归档", min_width=64, on_click=self.toggle_archive),
                        Button("删除", min_width=64, on_click=self.delete_note),
                    ],
                ),
            ],
        )

        self.root = Row(
            align="stretch",
            spacing=0,
            nodes=[
                Column(flex=0, padding=12, spacing=8, nodes=sidebar_nodes),
                Box(width=1, flex=0, color="#333355"),
                Column(
                    flex=1,
                    padding=12,
                    spacing=8,
                    nodes=[
                        Text("笔记列表", font_size=15, bold=True),
                        Row(
                            spacing=8,
                            align="stretch",
                            nodes=[
                                TextInput(
                                    "",
                                    flex=1,
                                    placeholder="搜索标题或正文…",
                                    id="search",
                                    on_submit=self.run_search,
                                ),
                                Button("搜", min_width=48, on_click=self.run_search),
                            ],
                        ),
                        ForEach(
                            self.display,
                            self.note_row,
                            updater=self.sync_note_row,
                            spacing=6,
                            scroll=True,
                            flex=1,
                            empty="（没有匹配的笔记）",
                        ),
                    ],
                ),
                Box(width=1, flex=0, color="#333355"),
                Column(
                    flex=1,
                    padding=12,
                    spacing=8,
                    nodes=[
                        Text("编辑", font_size=15, bold=True),
                        editor_card,
                    ],
                ),
            ],
        )

    def _editor_meta(self) -> str:
        note = self._selected()
        if note is None:
            return "未选中笔记"
        ts = datetime.datetime.fromtimestamp(note.updated).strftime("%Y-%m-%d %H:%M")
        flags = []
        if note.starred:
            flags.append("★")
        if note.archived:
            flags.append("归档")
        flag = " · ".join(flags)
        return f"{note.tag} · 更新 {ts}" + (f" · {flag}" if flag else "")


if __name__ == "__main__":
    NotesApp()
