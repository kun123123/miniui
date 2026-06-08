"""QPropertyAnimation 驱动 paint 偏移，layout rect 保持不变。"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PyQt6.QtCore import QEasingCurve, QObject, QPropertyAnimation, pyqtProperty

from .geometry import Rect

if TYPE_CHECKING:
    from .canvas import UiCanvas
    from .node import Node


@dataclass
class AnimStep:
    """动画句子里的一步：target 为节点或 id 字符串。"""

    target: str | Node
    dx: float | tuple[float, float] | None = None
    dy: float | tuple[float, float] | None = None
    duration: int = 350
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic
    reset_on_finish: bool | None = None


class _FloatAnimTarget(QObject):
    def __init__(self, value: float, on_change: Callable[[float], None]) -> None:
        super().__init__()
        self._value = value
        self._on_change = on_change

    def get_value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        self._value = value
        self._on_change(value)

    value = pyqtProperty(float, get_value, set_value)


def _normalize_axis(
    node: Node,
    attr: str,
    value: float | tuple[float, float] | None,
) -> tuple[float, float] | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        current = float(getattr(node, attr))
        return (current, float(value))
    start, end = value
    return (float(start), float(end))


def animate_float(
    canvas: UiCanvas,
    node: Node,
    *,
    attr: str,
    start: float,
    end: float,
    duration: int = 350,
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    reset_on_finish: bool = True,
    on_finished: Callable[[], None] | None = None,
) -> QPropertyAnimation:
    """对 node.paint_dx / paint_dy 做属性动画，每帧 merge_damage + _flush_repaint（内部 _resolve_dirty_damage）。"""
    # 记录零偏移时的可见区域；避免 caller 提前设为 start 导致首帧 old==new、原位置残留
    saved_dx, saved_dy = node.paint_dx, node.paint_dy
    node.paint_dx, node.paint_dy = 0.0, 0.0
    at_rest_paint = canvas._node_screen_rect(node)
    node.paint_dx, node.paint_dy = saved_dx, saved_dy

    first = [True]

    def apply(v: float) -> None:
        old_paint = canvas._node_screen_rect(node)
        slot = canvas._node_layout_screen_rect(node)
        setattr(node, attr, v)
        new_paint = canvas._node_screen_rect(node)
        damage = Rect.union(Rect.union(slot, old_paint), new_paint)
        if first[0]:
            first[0] = False
            damage = Rect.union(damage, at_rest_paint)
        node.merge_damage(damage)
        canvas._flush_repaint()

    target = _FloatAnimTarget(start, apply)
    anim = QPropertyAnimation(target, b"value")
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(easing)

    def _done() -> None:
        canvas._running_anims.remove(anim)
        # 终帧：擦掉原槽位 + 滑出后的可见区域，再交给 on_finished 删节点
        slot = canvas._node_layout_screen_rect(node)
        final = canvas._node_screen_rect(node)
        node.merge_damage(Rect.union(slot, final))
        canvas._flush_repaint(sync=False)
        if reset_on_finish:
            setattr(node, attr, 0.0)
        if on_finished is not None:
            on_finished()

    anim.finished.connect(_done)
    canvas._running_anims.append(anim)
    anim.start()
    return anim


def animate_sentence(
    canvas: UiCanvas,
    steps: Sequence[AnimStep],
    *,
    resolve_id: Callable[[str], Node] | None = None,
    on_finished: Callable[[], None] | None = None,
) -> None:
    """按顺序播放多步动画；中间步默认保留 paint 偏移，最后一步复位。"""
    if not steps:
        if on_finished is not None:
            on_finished()
        return

    pending = list(steps)

    def node_of(step: AnimStep) -> Node:
        target = step.target
        if not isinstance(target, str):
            return target
        if resolve_id is None:
            raise RuntimeError(f"字符串 target={target!r} 需要 resolve_id")
        return resolve_id(target)

    def run_next() -> None:
        if not pending:
            if on_finished is not None:
                on_finished()
            return
        step = pending.pop(0)
        node = node_of(step)
        is_last = len(pending) == 0
        reset = step.reset_on_finish if step.reset_on_finish is not None else is_last
        canvas.animate_offset(
            node,
            dx=_normalize_axis(node, "paint_dx", step.dx),
            dy=_normalize_axis(node, "paint_dy", step.dy),
            duration=step.duration,
            easing=step.easing,
            reset_on_finish=reset,
            on_finished=run_next,
        )

    run_next()
