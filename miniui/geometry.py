"""布局用的几何类型：位置、尺寸、矩形。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Size:
    width: float
    height: float

    @classmethod
    def zero(cls) -> Size:
        return cls(0.0, 0.0)


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px < self.right and self.y <= py < self.bottom
