"""Demo 15 · Image：路径 / QPixmap、固定尺寸与 fit。

运行（在 code/ui 目录下）：
    python demos/image.py

验收点：
  - 左：contain 在 140×100 槽内居中，保持比例
  - 中：fill 拉伸铺满
  - 右：cover 裁切铺满
  - 底：从 demos/assets/sample.png 加载（首次运行自动生成）
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtGui import QColor, QImage, QPainter, QPixmap

from miniui import App, Column, Image, Row, Text, Theme, run

_ASSETS = Path(__file__).resolve().parent / "assets"
_SAMPLE = _ASSETS / "image.png"


def _ensure_sample_png() -> Path:
    _ASSETS.mkdir(parents=True, exist_ok=True)
    if _SAMPLE.is_file():
        return _SAMPLE
    img = QImage(160, 100, QImage.Format.Format_ARGB32)
    img.fill(QColor("#3949ab"))
    p = QPainter(img)
    p.setPen(QColor("#e8eaf6"))
    p.drawRect(12, 12, 136, 76)
    p.drawText(24, 58, "MiniUI")
    p.end()
    img.save(str(_SAMPLE))
    return _SAMPLE


def _badge_pixmap() -> QPixmap:
    pm = QPixmap(96, 64)
    pm.fill(QColor("#00897b"))
    p = QPainter(pm)
    p.setPen(QColor("#ffffff"))
    p.drawText(20, 40, "PM")
    p.end()
    return pm


@run(title="Demo 15 · image", size=(520, 320), theme=Theme.dark())
class ImageDemo(App):
    def ui(self) -> None:
        badge = _badge_pixmap()
        sample = _ensure_sample_png()
        self.root = Column(
            padding=16,
            spacing=12,
            nodes=[
                Text("fit: contain · fill · cover（同一张 96×64）"),
                Row(
                    spacing=12,
                    align="stretch",
                    nodes=[
                        Image(badge, width=140, height=100, fit="contain"),
                        Image(badge, width=140, height=100, fit="fill"),
                        Image(badge, width=140, height=100, fit="cover"),
                    ],
                ),
                Text(f"文件: {sample.name}"),
                Image(str(sample), width=320, height=120, fit="contain"),
            ],
        )


if __name__ == "__main__":
    ImageDemo()
