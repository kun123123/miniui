"""Demo 17 · Video：本地视频播放、fit 与播放控制。

运行（在 code/ui 目录下）：
    python demos/video.py

验收点：
  - 自动播放（默认静音）
  - 「暂停 / 播放 / 停止」按钮生效
  - fit="contain" 在固定槽位内保持比例
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import App, Button, Column, Row, Text, Theme, Video, run

_VIDEO = Path(__file__).resolve().parent / "assets" / "sample.mp4"


@run(title="Demo 17 · video", size=(520, 420), theme=Theme.dark())
class VideoDemo(App):
    def ui(self) -> None:
        clip = Video(
            str(_VIDEO),
            width=480,
            height=270,
            fit="contain",
            autoplay=True,
            loop=True,
            muted=True,
        )
        self.root = Column(
            padding=16,
            spacing=12,
            nodes=[
                Text(f"文件: {_VIDEO.name}"),
                clip,
                Row(
                    spacing=8,
                    nodes=[
                        Button("播放", on_click=clip.play),
                        Button("暂停", on_click=clip.pause),
                        Button("停止", on_click=clip.stop),
                    ],
                ),
            ],
        )


if __name__ == "__main__":
    VideoDemo()
