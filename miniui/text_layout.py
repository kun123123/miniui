"""文本在有限宽度内的显示处理。"""

from __future__ import annotations

from typing import Literal

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics

OverflowMode = Literal["visible", "ellipsis", "clip"]


def fit_text_to_width(
    fm: QFontMetrics,
    text: str,
    max_width: float,
    mode: OverflowMode,
) -> str:
    """按 overflow 模式把 text 适配到 max_width 内（仅影响绘制串）。"""
    if mode == "visible":
        return text
    if not text or max_width <= 0:
        return ""
    if fm.horizontalAdvance(text) <= max_width:
        return text
    if mode == "ellipsis":
        return fm.elidedText(text, Qt.TextElideMode.ElideRight, max(1, int(max_width)))

    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if fm.horizontalAdvance(text[:mid]) <= max_width:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]
