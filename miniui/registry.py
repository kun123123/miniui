"""DSL：节点 id 注册与 ForEach 行内 id 映射。"""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dsl import AppCtx
    from .node import Node

_current_ctx: ContextVar[AppCtx | None] = ContextVar("miniui_app_ctx", default=None)


def get_current_ctx() -> AppCtx | None:
    return _current_ctx.get()


def set_current_ctx(ctx: AppCtx | None):
    return _current_ctx.set(ctx)


def reset_current_ctx(token) -> None:
    _current_ctx.reset(token)


def bind_ui_id(node: Node, ui_id: str | None) -> None:
    if not ui_id:
        return
    node.ui_id = ui_id
    ctx = _current_ctx.get()
    if ctx is None or ctx.in_foreach_builder:
        return
    ctx.register_id(ui_id, node)


def collect_id_map(root: Node) -> None:
    """ForEach 每行构建完成后，在根节点上挂 id → Node 映射供 animate 解析。"""
    id_map: dict[str, Node] = {}
    for n in root.iter_subtree():
        uid = getattr(n, "ui_id", None)
        if uid:
            id_map[uid] = n
    root._id_map = id_map
