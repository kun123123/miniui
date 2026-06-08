"""Row / Column 工厂：``Row(padding=16, nodes=[ Box(), Text() ])``。"""

from __future__ import annotations

from collections.abc import Sequence

from .column import Column as _Column, Panel as _Panel
from .node import Node
from .row import Row as _Row
from .stack import Stack as _Stack

_LAYOUT = frozenset(
    {
        "padding",
        "spacing",
        "align",
        "flex",
        "margin",
        "id",
        "children",
        "color",
        "radius",
        "overlay_anchor",
    }
)


def _extend_nodes(all_nodes: list[Node], node_group: Sequence[Node]) -> None:
    if isinstance(node_group, (set, frozenset)):
        raise TypeError(
            "nodes= 请用 list [...] 或 tuple (...)，不要用 { ... }："
            "set 无序，Row/Column 子组件顺序会乱"
        )
    all_nodes.extend(node_group)


def _container(cls: type[Node], *nodes: Node, **kwargs) -> Node:
    layout: dict = {}
    all_nodes = list(nodes)

    children = kwargs.pop("children", None)
    if children is not None:
        all_nodes = list(children) + all_nodes

    node_group = kwargs.pop("nodes", None)
    if node_group is not None:
        _extend_nodes(all_nodes, node_group)

    for key, value in kwargs.items():
        if key in _LAYOUT:
            layout[key] = value
        elif isinstance(value, Node):
            all_nodes.append(value)
        else:
            raise TypeError(f"未知参数 {key!r}={value!r}（布局键、nodes= 或 Node）")

    return cls(*all_nodes, **layout)


def Row(*nodes: Node, **kwargs) -> _Row:
    """属性写在前，子组件写在 ``nodes=[ ... ]`` 里（有序，不要用 set ``{...}``）。"""
    return _container(_Row, *nodes, **kwargs)


def Column(*nodes: Node, **kwargs) -> _Column:
    return _container(_Column, *nodes, **kwargs)


def Panel(*nodes: Node, **kwargs) -> _Panel:
    return _container(_Panel, *nodes, **kwargs)


def Stack(*nodes: Node, **kwargs) -> _Stack:
    return _container(_Stack, *nodes, **kwargs)
