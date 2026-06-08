"""MiniPlayer · 本地视频播放器（MiniUI 示例应用）。

运行（在 code/ui 目录下）：
    python demos/player_app.py

能力：
  - 视频铺满窗口 · 底部控制条悬浮叠放
  - 鼠标移动显示控制条 · 离开控制条 1s 后自动隐藏
  - 打开本地视频 · 进度跳转 · 音量调节
"""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFileDialog

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from miniui import (
    App,
    Button,
    DerivedText,
    Panel,
    Row,
    SeekBar,
    Spacer,
    Stack,
    Text,
    Theme,
    Video,
    run,
)

_DEFAULT = Path(__file__).resolve().parent / "assets" / "sample.mp4"
_FILTERS = "视频 (*.mp4 *.mkv *.avi *.mov *.webm *.wmv);;所有文件 (*)"
_PANEL_OVERLAY = "#e6222438"
_CTRL_H = 36
_HIDE_MS = 1000


def _fmt_ms(ms: int) -> str:
    if ms < 0:
        ms = 0
    s, _ = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def _ctrl_btn(label: str, *, on_click=None, min_width: float = 40) -> Button:
    return Button(
        label,
        min_width=min_width,
        height=_CTRL_H,
        on_click=on_click,
    )


@run(title="MiniPlayer", size=(960, 540), theme=Theme.dark())
class PlayerApp(App):
    _clip: Video | None = None
    _controls: Panel | None = None
    _seek: SeekBar | None = None
    _play_btn: Button | None = None
    _mute_btn: Button | None = None
    _title_text: Text | None = None
    _seeking = False

    def mount(self, ctx) -> None:
        super().mount(ctx)
        self.file_path = ctx.state(str(_DEFAULT))
        self.tick = ctx.state(0)

    def ui(self) -> None:
        path = Path(self.file_path.value)
        self._clip = Video(
            self.file_path.value,
            fit="contain",
            autoplay=True,
            loop=False,
            muted=False,
        )
        self._seek = SeekBar(on_seek=self._on_seek)
        self._play_btn = _ctrl_btn("⏸", min_width=44, on_click=self._toggle_play)
        self._mute_btn = _ctrl_btn("🔊", min_width=44, on_click=self._toggle_mute)
        self._title_text = Text(path.name, font_size=14, bold=True, overflow="ellipsis")

        self._controls = Panel(
            padding=16,
            spacing=12,
            align="stretch",
            color=_PANEL_OVERLAY,
            radius=0,
            overlay_anchor="bottom",
            nodes=[
                self._title_text,
                Row(
                    spacing=12,
                    align="stretch",
                    nodes=[
                        DerivedText(
                            lambda: _fmt_ms(self._clip.position if self._clip else 0),
                            deps=[self.tick],
                            font_size=12,
                        ),
                        self._seek,
                        DerivedText(
                            lambda: _fmt_ms(self._clip.duration if self._clip else 0),
                            deps=[self.tick],
                            font_size=12,
                        ),
                    ],
                ),
                Row(
                    spacing=6,
                    align="center",
                    nodes=[
                        _ctrl_btn("打开", min_width=52, on_click=self._open_file),
                        self._play_btn,
                        _ctrl_btn("⏹", min_width=44, on_click=self._stop),
                        _ctrl_btn("−10s", min_width=48, on_click=lambda: self._skip(-10_000)),
                        _ctrl_btn("+10s", min_width=48, on_click=lambda: self._skip(10_000)),
                        Spacer(flex=1),
                        _ctrl_btn("−", min_width=36, on_click=lambda: self._adjust_volume(-0.1)),
                        _ctrl_btn("+", min_width=36, on_click=lambda: self._adjust_volume(0.1)),
                        self._mute_btn,
                    ],
                ),
            ],
        )

        self.root = Stack(nodes=[self._clip, self._controls])

    def on_ready(self) -> None:
        self._timer = QTimer()
        self._timer.timeout.connect(self._sync_ui)
        self._timer.start(200)

        self._hide_timer = QTimer()
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._hide_controls)

        if self.ctx and self.ctx.canvas is not None:
            self.ctx.canvas.set_mouse_move_handler(self._on_mouse_move)

        if self._controls is not None:
            self._controls.visible = False

        self._sync_ui()

    def _on_mouse_move(self, x: float, y: float) -> None:
        self._show_controls()
        if self._controls_contains(x, y):
            self._hide_timer.stop()
        else:
            self._hide_timer.start(_HIDE_MS)

    def _controls_contains(self, x: float, y: float) -> bool:
        if self._controls is None or not self._controls.visible:
            return False
        canvas = self.ctx.canvas if self.ctx else None
        if canvas is None:
            return False
        return canvas._node_screen_rect(self._controls).contains(x, y)

    def _show_controls(self) -> None:
        if self._controls is None:
            return
        if self._controls.visible:
            return
        self._controls.visible = True
        self._controls.mark_paint_dirty()
        if self.ctx and self.ctx.canvas is not None:
            self.ctx.canvas._schedule_update()
        self._sync_ui()

    def _hide_controls(self) -> None:
        if self._controls is None or not self._controls.visible:
            return
        self._controls.visible = False
        if self._clip is not None:
            self._clip._repaint_video_area()

    def _repaint_controls(self) -> None:
        if self._controls is None or not self._controls.visible:
            return
        canvas = self.ctx.canvas if self.ctx else None
        if canvas is None:
            return
        self._controls.set_damage(canvas._node_screen_rect(self._controls))
        canvas._schedule_update()

    def _sync_ui(self) -> None:
        if self._clip is None:
            return
        if self._controls is None or not self._controls.visible:
            return
        if self._seek is not None and not self._seeking and self._clip.duration > 0:
            ratio = self._clip.position / self._clip.duration
            if abs(self._seek.progress - ratio) > 0.003:
                self._seek.progress = ratio
                self._repaint_controls()
        if self._play_btn is not None:
            label = "⏸" if self._clip.playing else "▶"
            if self._play_btn.label != label:
                self._play_btn.label = label
        if self._mute_btn is not None:
            label = "🔇" if self._clip.muted else "🔊"
            if self._mute_btn.label != label:
                self._mute_btn.label = label
        self.tick.update()

    def _on_seek(self, ratio: float) -> None:
        if self._clip is None:
            return
        self._seeking = True
        self._clip.seek_ratio(ratio)
        if self._seek is not None:
            self._seek.progress = ratio
            self._repaint_controls()
        self._seeking = False
        self.tick.update()
        self._hide_timer.stop()
        self._hide_timer.start(_HIDE_MS)

    def _toggle_play(self) -> None:
        if self._clip is not None:
            self._clip.toggle_play_pause()
            self._sync_ui()

    def _stop(self) -> None:
        if self._clip is not None:
            self._clip.stop()
        if self._seek is not None:
            self._seek.progress = 0.0
            self._seek.mark_paint_dirty()
        self._sync_ui()

    def _skip(self, delta_ms: int) -> None:
        if self._clip is not None:
            self._clip.skip(delta_ms)
            self._sync_ui()

    def _adjust_volume(self, delta: float) -> None:
        if self._clip is None:
            return
        self._clip.volume = self._clip.volume + delta
        if self._clip.volume <= 0:
            self._clip.muted = True
        elif self._clip.muted and delta > 0:
            self._clip.muted = False
        self._sync_ui()

    def _toggle_mute(self) -> None:
        if self._clip is None:
            return
        self._clip.muted = not self._clip.muted
        self._sync_ui()

    def _open_file(self) -> None:
        start = str(Path(self.file_path.value).parent)
        path, _ = QFileDialog.getOpenFileName(None, "选择视频", start, _FILTERS)
        if not path:
            return
        self.file_path.set(path)
        if self._clip is not None:
            self._clip.autoplay = True
            self._clip.source = path
            self._clip.play()
        if self._title_text is not None:
            self._title_text.text = Path(path).name
        if self._seek is not None:
            self._seek.progress = 0.0
            self._seek.mark_paint_dirty()
        self._sync_ui()
        self._show_controls()
        self._hide_timer.stop()
        self._hide_timer.start(_HIDE_MS)


if __name__ == "__main__":
    PlayerApp()
