"""QPropertyAnimation 驱动 paint 偏移，layout rect 保持不变。"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtCore import QEasingCurve, QObject, QPropertyAnimation, pyqtProperty

from .geometry import Rect

if TYPE_CHECKING:
    from .canvas import UiCanvas
    from .node import Node


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


def animate_float(
    canvas: UiCanvas,
    node: Node,
    *,
    attr: str,
    start: float,
    end: float,
    duration: int = 350,
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
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
        node.paint_dx = 0.0
        node.paint_dy = 0.0
        if on_finished is not None:
            on_finished()

    anim.finished.connect(_done)
    canvas._running_anims.append(anim)
    anim.start()
    return anim
