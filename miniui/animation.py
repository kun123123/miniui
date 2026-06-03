"""QPropertyAnimation 驱动 paint 偏移，layout rect 保持不变。"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtCore import QEasingCurve, QObject, QPropertyAnimation, pyqtProperty

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
    """对 node.paint_dx / paint_dy 做属性动画，每帧触发 canvas.update()。"""

    def apply(v: float) -> None:
        setattr(node, attr, v)
        node.mark_paint_dirty()
        canvas.update()

    target = _FloatAnimTarget(start, apply)
    anim = QPropertyAnimation(target, b"value")
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(easing)

    def _done() -> None:
        canvas._running_anims.remove(anim)
        if on_finished is not None:
            on_finished()

    anim.finished.connect(_done)
    canvas._running_anims.append(anim)
    anim.start()
    return anim
