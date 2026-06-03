"""with 块 UI 构建：块内创建的 Node 自动挂到当前容器。"""

from __future__ import annotations

from contextvars import ContextVar, Token

from .node import Node

_stack: ContextVar[tuple[Node, ...]] = ContextVar("miniui_ui_stack", default=())


class UiScope:
    """供 Column / Row / ScrollView 混入：支持 ``with Container():`` 写法。"""

    def __enter__(self) -> Node:
        self._ui_token: Token = _stack.set(_stack.get() + (self,))
        return self

    def __exit__(self, *_exc) -> bool:
        _stack.reset(self._ui_token)
        return False


def auto_mount(node: Node) -> None:
    """Node 构造结束时调用：若处于 with 块内则自动 add_child。"""
    stack = _stack.get()
    if not stack:
        return
    parent = stack[-1]
    if parent is node:
        return
    if node.parent is not None:
        return
    from .scroll import ScrollView

    if isinstance(parent, ScrollView):
        parent.set_child(node)
    elif hasattr(parent, "add_child"):
        parent.add_child(node)
    else:
        raise TypeError(f"{type(parent).__name__} 不支持 with 块挂载子节点")
