"""DSL：@run 入口、DerivedText / ForEach、ctx.state / ctx.animate。"""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from typing import TypeVar

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from .animation import AnimStep
from .canvas import UiCanvas
from .column import Column
from .node import Node
from .registry import collect_id_map, reset_current_ctx, set_current_ctx
from .row import Row
from .scroll import ScrollView
from .state import Bindings, State
from .text_layout import OverflowMode
from .theme import Theme
from .widgets import Text, TextInput

T = TypeVar("T")


class App:
    """基于 class 的应用：``mount`` 写逻辑，``ui`` 里 ``self.root = ...``。"""

    root: Node | None = None
    ctx: AppCtx | None = None

    def mount(self, ctx: AppCtx) -> None:
        """逻辑层：state、数据、回调注册。"""
        self.ctx = ctx

    def ui(self) -> None:
        """描述层：构建界面，赋值 ``self.root``（不要 return）。"""
        raise NotImplementedError

    def on_ready(self) -> None:
        """窗口就绪后可选钩子（如默认聚焦输入框）。"""

    def build(self, ctx: AppCtx) -> Node:
        self.root = None
        self.mount(ctx)
        self.ui()
        if self.root is None:
            raise RuntimeError(f"{type(self).__name__}.ui() 必须设置 self.root")
        return self.root


class AppCtx:
    """@run 回调上下文：state、id 引用、主题与动画。"""

    def __init__(self, theme: Theme, *, starts_dark: bool = True) -> None:
        self._theme = theme
        self._is_dark = starts_dark
        self._app_ids: dict[str, Node] = {}
        self.canvas: UiCanvas | None = None
        self.in_foreach_builder = False

    def state(self, value: T) -> State[T]:
        return State(value)

    def register_id(self, name: str, node: Node) -> None:
        self._app_ids[name] = node

    def ref(self, name: str) -> Node:
        return self._app_ids[name]

    def __getattr__(self, name: str) -> Node:
        if name.startswith("_") or name in ("canvas", "state", "ref", "animate", "animate_sentence"):
            raise AttributeError(name)
        try:
            return self._app_ids[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def attach(self, canvas: UiCanvas) -> None:
        self.canvas = canvas

    def set_theme(self, theme: Theme) -> None:
        self._theme = theme
        if self.canvas is not None:
            self.canvas.set_theme(theme)

    def toggle_theme(self) -> None:
        self._is_dark = not self._is_dark
        self.set_theme(Theme.dark() if self._is_dark else Theme.light())

    def animate(
        self,
        target: str | Node,
        *,
        dx: tuple[float, float] | None = None,
        dy: tuple[float, float] | None = None,
        duration: int = 350,
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        if self.canvas is None:
            raise RuntimeError("canvas 尚未挂载")
        node = target if isinstance(target, Node) else self._resolve_id(target)
        self.canvas.animate_offset(
            node,
            dx=dx,
            dy=dy,
            duration=duration,
            on_finished=on_finished,
        )

    def animate_sentence(
        self,
        steps: Sequence[AnimStep],
        *,
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        """串行播放动画句子：上抬 → 横移 → 落回 等多步组合。"""
        if self.canvas is None:
            raise RuntimeError("canvas 尚未挂载")
        self.canvas.animate_sentence(
            list(steps),
            resolve_id=self._resolve_id,
            on_finished=on_finished,
        )

    def _resolve_id(self, name: str) -> Node:
        if name in self._app_ids:
            return self._app_ids[name]
        source = getattr(self.canvas, "_last_event_node", None)
        node: Node | None = source
        while node is not None:
            id_map = getattr(node, "_id_map", None)
            if id_map is not None and name in id_map:
                return id_map[name]
            node = node.parent
        raise KeyError(f"未找到 id={name!r}（应用级或当前行内）")


def DerivedText(
    getter: Callable[[], str],
    *,
    deps: list[State],
    font_size: int = 14,
    bold: bool = False,
    flex: float = 0,
    margin: float = 0,
    overflow: OverflowMode = "visible",
    id: str | None = None,
) -> Text:
    """派生文本：deps 变化时自动刷新。"""
    node = Text(
        "",
        font_size=font_size,
        bold=bold,
        flex=flex,
        margin=margin,
        overflow=overflow,
        id=id,
    )
    node._derived_meta = (getter, deps)
    node._derived_paint_only = True
    return node


def ForEach(
    state: State,
    builder: Callable[..., Node],
    *,
    updater: Callable[[Node, T], None] | None = None,
    spacing: float = 8,
    scroll: bool = True,
    flex: float = 1,
    empty: str = "（没有匹配的任务）",
) -> Node:
    col = Column(spacing=spacing, align="stretch")
    if scroll:
        view = ScrollView(flex=flex, child=col)
        view._foreach_meta = (state, builder, col, view, empty, updater)
        return view
    col.flex = flex
    col._foreach_meta = (state, builder, col, None, empty, updater)
    return col


def _wire_tree(ctx: AppCtx, canvas: UiCanvas, root: Node) -> None:
    bindings = Bindings(canvas)
    for node in root.iter_subtree():
        derived = getattr(node, "_derived_meta", None)
        if derived is None:
            continue
        getter, deps = derived
        bindings.text(node, getter, *deps)

    for node in root.iter_subtree():
        foreach = getattr(node, "_foreach_meta", None)
        if foreach is None:
            continue
        state, builder, col, scroll_view, empty, updater = foreach

        def wrap(b: Callable[..., Node]) -> Callable[..., Node]:
            def built(item):
                ctx.in_foreach_builder = True
                try:
                    row = b(item)
                    collect_id_map(row)
                    return row
                finally:
                    ctx.in_foreach_builder = False

            return built

        bindings.list(
            col,
            lambda s=state: s.value,
            wrap(builder),
            state,
            scroll=scroll_view,
            empty=empty,
            updater=updater,
        )


def _launch(
    *,
    ctx: AppCtx,
    root: Node,
    window_title: str,
    size: tuple[int, int],
    app_theme: Theme,
    app_instance: App | None = None,
) -> None:
    canvas = UiCanvas(theme=app_theme, root=root)
    ctx.attach(canvas)
    _wire_tree(ctx, canvas, root)

    window = QMainWindow()
    window.setWindowTitle(window_title)
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(*size)
    window.show()
    canvas.relayout(force=True)
    if app_instance is not None:
        app_instance.on_ready()
    sys.exit(QApplication.instance().exec())


def run(
    *,
    title: str | None = None,
    size: tuple[int, int] = (640, 480),
    theme: Theme | None = None,
):
    """装饰 App 子类或 ``def app(ctx): return root``，负责 Qt 窗口与事件循环。"""

    def decorator(target: type[App] | Callable[[AppCtx], Node]) -> Callable[[], None]:
        if isinstance(target, type):
            if not issubclass(target, App):
                raise TypeError("@run  class 必须继承 miniui.App")
            app_cls = target
            window_title = title or app_cls.__name__

            def build(ctx: AppCtx) -> Node:
                return app_cls().build(ctx)

            def main() -> None:
                qt_app = QApplication(sys.argv)
                app_theme = theme or Theme.dark()
                ctx = AppCtx(app_theme, starts_dark=theme is None or theme is not Theme.light())
                instance = app_cls()
                token = set_current_ctx(ctx)
                try:
                    root = instance.build(ctx)
                finally:
                    reset_current_ctx(token)
                _launch(
                    ctx=ctx,
                    root=root,
                    window_title=window_title,
                    size=size,
                    app_theme=app_theme,
                    app_instance=instance,
                )

            main.__doc__ = app_cls.__doc__
            main.__name__ = app_cls.__name__
            main.build = build
            main.app_cls = app_cls
            return main

        fn = target
        window_title = title or fn.__name__

        def main() -> None:
            qt_app = QApplication(sys.argv)
            app_theme = theme or Theme.dark()
            ctx = AppCtx(app_theme, starts_dark=theme is None or theme is not Theme.light())
            token = set_current_ctx(ctx)
            try:
                root = fn(ctx)
            finally:
                reset_current_ctx(token)
            _launch(
                ctx=ctx,
                root=root,
                window_title=window_title,
                size=size,
                app_theme=app_theme,
            )

        main.__doc__ = fn.__doc__
        main.__name__ = fn.__name__
        main.build = fn
        return main

    return decorator
