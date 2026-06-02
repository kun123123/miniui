"""父节点传给子节点的尺寸约束。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Constraints:
    max_width: float
    max_height: float

    @classmethod
    def loose(cls, max_width: float, max_height: float) -> Constraints:
        return cls(max_width, max_height)

    @classmethod
    def tight(cls, width: float, height: float) -> Constraints:
        return cls(width, height)
