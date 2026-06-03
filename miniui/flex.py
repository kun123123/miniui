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


def apply_flex(
    children: list[Node],
    sizes: list[Size],
    *,
    axis: Axis,
    inner_main: float,
    spacing: float,
) -> list[Size]:
    """把主轴上的剩余空间按 flex 比例分给子节点。"""
    n = len(children)
    if n == 0:
        return sizes

    gap = spacing * max(0, n - 1)
    flex_sum = sum(c.flex for c in children if c.flex > 0)
    if flex_sum <= 0:
        return sizes

    fixed = 0.0
    flex_used = 0.0
    for child, size in zip(children, sizes):
        m = _main(size, axis)
        if child.flex > 0:
            flex_used += m
        else:
            fixed += m

    remaining = max(0.0, inner_main - fixed - flex_used - gap)
    result = list(sizes)
    for i, child in enumerate(children):
        if child.flex <= 0:
            continue
        share = remaining * (child.flex / flex_sum)
        result[i] = _set_main(result[i], axis, _main(result[i], axis) + share)
    return result


def measure_children(
    children: list[Node],
    *,
    axis: Axis,
    inner_cross: float,
    inner_main: float,
    spacing: float,
) -> list[Size]:
    """
    先量固定子节点，再用「剩余主轴空间」量 flex 子节点，最后 apply_flex。

    避免 flex 子节点在 measure 时占用父级全宽/全高，layout 时被压窄导致溢出。
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
        if axis == "horizontal":
            c = Constraints.loose(inner_main, inner_cross)
        else:
            c = Constraints.loose(inner_cross, inner_main)
        sizes[i] = child._measure_with_margin(c)
        fixed_main += _main(sizes[i], axis)

    flex_main = max(0.0, inner_main - fixed_main - gap)
    for i, child in enumerate(children):
        if child.flex <= 0:
            continue
        if axis == "horizontal":
            c = Constraints.loose(flex_main, inner_cross)
        else:
            c = Constraints.loose(inner_cross, flex_main)
        sizes[i] = child._measure_with_margin(c)

    if any(c.flex > 0 for c in children):
        sizes = apply_flex(
            children, sizes, axis=axis, inner_main=inner_main, spacing=spacing
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
