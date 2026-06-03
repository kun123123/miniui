# MiniUI

PyQt6 自绘 UI 教学框架：`measure → layout → paint` 三遍 pass，单画布 `UiCanvas` + 渲染树。

原理长文：[MiniUI：从零理解渲染树、布局与绘制](https://nimble-cocada-736242.netlify.app/category/gui/miniui-framework/)（本地 `blog/src/content/blog/miniui-framework.md`）。

## 安装

```bash
cd code/ui
pip install -r requirements.txt
```

## 快速开始

```bash
python demos/minimal_app.py    # Demo 01 · 最小窗口
python demos/demo_app.py       # Demo 13 · 综合待办
```

## 分步 Demo

| # | 命令 | 主题 |
|---|------|------|
| 01 | `python demos/minimal_app.py` | 最小可运行 |
| 02 | `python demos/button.py` | Button + 自动重绘 |
| 03 | `python demos/flex.py` | flex |
| 04 | `python demos/padding.py` | padding / spacing |
| 05 | `python demos/spacer.py` | Spacer |
| 06 | `python demos/box.py` | Box |
| 07 | `python demos/text_input.py` | TextInput |
| 08 | `python demos/ellipsis.py` | Text 省略号 |
| 09 | `python demos/scroll.py` | ScrollView |
| 10 | `python demos/state.py` | State + Bindings |
| 11 | `python demos/animation.py` | animate_offset |
| 12 | `python demos/theme.py` | 换肤 |
| 13 | `python demos/demo_app.py` | 综合演示 |

验收说明与 docstring 见 **[demos/README.md](demos/README.md)**。

## 目录

```text
miniui/       框架核心（Node、Column/Row、ScrollView、State…）
demos/        13 个分步示例
docs/         原理笔记，见 docs/README.md
```

## License

MIT
