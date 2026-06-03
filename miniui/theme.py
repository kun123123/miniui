"""主题：颜色、字体、圆角集中定义，paint 时通过 get_theme() 读取。"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field

from .geometry import Rect


@dataclass(frozen=True)
class ThemeColors:
    canvas_bg: str
    text_primary: str
    text_muted: str
    button_fg: str
    button_border: str
    button_bg: str
    button_border_pressed: str
    button_bg_pressed: str
    input_bg: str
    input_text: str
    input_border: str
    input_border_focused: str
    input_caret: str
    box_fill: str
    box_label: str


@dataclass(frozen=True)
class ThemeFonts:
    family: str = "Microsoft YaHei"
    size_body: int = 13


@dataclass(frozen=True)
class ThemeMetrics:
    radius: int = 6
    input_height: float = 32
    button_height: float = 32
    input_padding_x: float = 8


@dataclass(frozen=True)
class Theme:
    colors: ThemeColors
    fonts: ThemeFonts = field(default_factory=ThemeFonts)
    metrics: ThemeMetrics = field(default_factory=ThemeMetrics)

    @staticmethod
    def light() -> Theme:
        return Theme(
            colors=ThemeColors(
                canvas_bg="#fafafa",
                text_primary="#1e1e1e",
                text_muted="#a0a0aa",
                button_fg="#28325a",
                button_border="#6478c8",
                button_bg="#ebf0ff",
                button_border_pressed="#5064b4",
                button_bg_pressed="#d2dcf5",
                input_bg="#ffffff",
                input_text="#1e1e1e",
                input_border="#c8cdd7",
                input_border_focused="#a0aac8",
                input_caret="#3c5ac8",
                box_fill="#e8eef8",
                box_label="#3c3c50",
            ),
        )

    @staticmethod
    def dark() -> Theme:
        return Theme(
            colors=ThemeColors(
                canvas_bg="#1a1a1e",
                text_primary="#e8e8ec",
                text_muted="#888894",
                button_fg="#dce4ff",
                button_border="#5a6aa0",
                button_bg="#2a3048",
                button_border_pressed="#7890d0",
                button_bg_pressed="#3a4468",
                input_bg="#252530",
                input_text="#e8e8ec",
                input_border="#404050",
                input_border_focused="#6070a8",
                input_caret="#7090e8",
                box_fill="#2a3040",
                box_label="#b0b0bc",
            ),
        )


_default_theme = Theme.light()
_theme_ctx: ContextVar[Theme | None] = ContextVar("miniui_theme", default=None)


def get_theme() -> Theme:
    theme = _theme_ctx.get()
    return theme if theme is not None else _default_theme


def push_theme(theme: Theme) -> Token:
    return _theme_ctx.set(theme)


def pop_theme(token: Token) -> None:
    _theme_ctx.reset(token)


def fill_canvas_rect(painter, region: Rect) -> None:
    """用当前主题画布色填充区域（与 paintEvent clip 对齐，float 边界）。"""
    from PyQt6.QtCore import QRectF
    from PyQt6.QtGui import QColor

    bg = QColor(get_theme().colors.canvas_bg)
    painter.fillRect(QRectF(region.x, region.y, region.width, region.height), bg)
