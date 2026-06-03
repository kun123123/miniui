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

    def intersects(self, other: Rect) -> bool:
        return not (
            self.right <= other.x
            or other.right <= self.x
            or self.bottom <= other.y
            or other.bottom <= self.y
        )

    def intersect(self, other: Rect) -> Rect | None:
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.right, other.right)
        y2 = min(self.bottom, other.bottom)
        if x2 <= x1 or y2 <= y1:
            return None
        return Rect(x1, y1, x2 - x1, y2 - y1)

    @classmethod
    def union(cls, a: Rect, b: Rect) -> Rect:
        """两矩形并集（覆盖二者及其中间空隙）。"""
        x1 = min(a.x, b.x)
        y1 = min(a.y, b.y)
        x2 = max(a.right, b.right)
        y2 = max(a.bottom, b.bottom)
        return cls(x1, y1, x2 - x1, y2 - y1)
