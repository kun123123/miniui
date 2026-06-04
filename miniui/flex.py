"""flex 剩余空间分配（Column 纵向 / Row 横向）。"""

from __future__ import annotations

from typing import Literal

from .constraints import Constraints
from .geometry import Size
from .node import Node

Axis = Literal["horizontal", "vertical"]


def _main(size: Size, axis: Axis) -> float:
    return size.width if axis == "horizontal" else size.height


def _set_main(size: Size, axis: Axis, value: float) -> Size:
    if axis == "horizontal":
        return Size(value, size.height)
    return Size(size.width, value)


def _child_constraints(
    axis: Axis, inner_main: float, inner_cross: float
) -> Constraints:
    if axis == "horizontal":
        return Constraints.loose(inner_main, inner_cross)
    return Constraints.loose(inner_cross, inner_main)


def measure_children(
    children: list[Node],
    *,
    axis: Axis,
    inner_cross: float,
    inner_main: float,
    spacing: float,
) -> list[Size]:
    """
    1. 先量 flex=0 的子节点（可用 fixed width/height），占满主轴「固定」部分。
    2. 剩余主轴长度按 flex 比例切成份额；flex>0 的子节点只在各自份额内 measure。
    3. 主轴槽位宽度 = 份额（与 intrinsic 无关）；交叉轴取 measure 结果。

    flex>0 时子节点上的 fixed width/height 不参与分配（见 Box 等 measure）。
    """
    n = len(children)
    if n == 0:
        return []

    gap = spacing * max(0, n - 1)
    sizes: list[Size] = [Size.zero() for _ in children]
    fixed_main = 0.0

    for i, child in enumerate(children):
        if child.flex > 0:
            continue
        sizes[i] = child._measure_with_margin(
            _child_constraints(axis, inner_main, inner_cross)
        )
        fixed_main += _main(sizes[i], axis)

    flex_sum = sum(c.flex for c in children if c.flex > 0)
    if flex_sum <= 0:
        return sizes

    remaining = max(0.0, inner_main - fixed_main - gap)
    for i, child in enumerate(children):
        if child.flex <= 0:
            continue
        share = remaining * (child.flex / flex_sum)
        measured = child._measure_with_margin(
            _child_constraints(axis, share, inner_cross)
        )
        cross = measured.height if axis == "horizontal" else measured.width
        sizes[i] = (
            Size(share, cross) if axis == "horizontal" else Size(cross, share)
        )
    return sizes


def content_main(
    children: list[Node],
    sizes: list[Size],
    *,
    axis: Axis,
    spacing: float,
) -> float:
    n = len(children)
    if n == 0:
        return 0.0
    total = sum(_main(s, axis) for s in sizes)
    return total + spacing * max(0, n - 1)
