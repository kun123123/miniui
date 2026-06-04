"""响应式 State：改值 → 订阅者自动同步 UI。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from .canvas import UiCanvas
from .column import Column
from .node import Node
from .scroll import ScrollView
from .widgets import Text

T = TypeVar("T")


class State(Generic[T]):
    """可订阅的可变数据源。"""

    def __init__(self, value: T) -> None:
        self._value = value
        self._subs: list[Callable[[], None]] = []

    @property
    def value(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        if value == self._value:
            return
        self._value = value
        self._notify()

    def update(self) -> None:
        """原地修改 ``value``（如 list.append）后调用，通知订阅者。"""
        self._notify()

    def subscribe(self, fn: Callable[[], None]) -> None:
        self._subs.append(fn)

    def _notify(self) -> None:
        for fn in self._subs:
            fn()


class Bindings:
    """把 State 绑到 Text / 列表容器，省掉手写 refresh。"""

    def __init__(self, canvas: UiCanvas) -> None:
        self.canvas = canvas

    def _queue_canvas_update(self) -> None:
        self.canvas._schedule_update()

    def text(
        self,
        node: Text,
        getter: Callable[[], str],
        *states: State,
    ) -> None:
        def apply() -> None:
            value = getter()
            if node._text == value:
                return
            node._text = value
            node._display_key = None
            if getattr(node, "_derived_paint_only", False):
                node.mark_paint_dirty()
            elif node.flex > 0 or node.overflow != "visible":
                node.mark_paint_dirty()
            else:
                node.mark_layout_dirty()

        for st in states:
            st.subscribe(apply)
        apply()

    def list(
        self,
        column: Column,
        getter: Callable[[], list],
        builder: Callable[..., Node],
        *states: State,
        scroll: ScrollView | None = None,
        empty: str = "（没有匹配的任务）",
        updater: Callable[[Node, object], None] | None = None,
    ) -> None:
        def _attach_item(row: Node, item: object) -> None:
            row._foreach_item = item

        def _full_rebuild(data: list) -> None:
            for child in list(column.children):
                column.remove_child(child)
            if data:
                for item in data:
                    row = builder(item)
                    _attach_item(row, item)
                    column.add_child(row)
            else:
                column.add_child(Text(empty, font_size=13))
            if scroll is not None:
                scroll.scroll_y = 0.0
                scroll._clamp_scroll()
                scroll.set_damage(self.canvas._node_screen_rect(scroll))
            self._queue_canvas_update()

        def _same_structure(data: list) -> bool:
            children = column.children
            if len(children) != len(data):
                return False
            return all(
                getattr(children[i], "_foreach_item", None) is data[i]
                for i in range(len(data))
            )

        def refresh() -> None:
            data = getter()
            if data and updater is not None and _same_structure(data):
                for row, item in zip(column.children, data):
                    updater(row, item)
                self._queue_canvas_update()
                return
            _full_rebuild(data)

        for st in states:
            st.subscribe(refresh)
        refresh()
