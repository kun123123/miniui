"""
UI 节点基类。

三遍 pass（和真实 UI 框架一致）：
  1. measure(constraints)  子 → 父汇报「我需要多大」
  2. layout(rect)          父 → 子分配最终矩形
  3. paint(painter)        按 rect 绘制
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .constraints import Constraints
from .geometry import Rect, Size

if TYPE_CHECKING:
    from PyQt6.QtGui import QPainter


class Node(ABC):
    def __init__(self) -> None:
        self.rect = Rect(0, 0, 0, 0)
        self.parent: Node | None = None

    @abstractmethod
    def measure(self, constraints: Constraints) -> Size:
        ...

    @abstractmethod
    def layout(self, rect: Rect) -> None:
        ...

    @abstractmethod
    def paint(self, painter: QPainter) -> None:
        ...

    def hit_test(self, x: float, y: float) -> Node | None:
        if not self.rect.contains(x, y):
            return None
        return self

    def dump(self, indent: int = 0) -> str:
        pad = "  " * indent
        r = self.rect
        lines = [
            f"{pad}{self.__class__.__name__} "
            f"rect=({r.x:.0f},{r.y:.0f},{r.width:.0f}x{r.height:.0f})"
        ]
        return "\n".join(lines)
