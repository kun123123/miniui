# MiniUI

PyQt6 教学用自绘 UI 框架：单画布 `UiCanvas` + `Node` 渲染树，三遍 pass（`measure` → `layout` → `paint`）。

- **博客长文**（原理与设计）[点击跳转](https://nimble-cocada-736242.netlify.app/)
- **独立仓库**：[github.com/kun123123/miniui](https://github.com/kun123123/miniui)

## 环境

```bash
cd code/ui
pip install -r requirements.txt
python demos/minimal_app.py
```

需 Python 3.10+、PyQt6。

## 应用写法（推荐）

```python
from miniui import App, Column, Text, Theme, run

@run(title="Hello", size=(400, 200), theme=Theme.dark())
class MyApp(App):
    def mount(self, ctx):
        super().mount(ctx)
        self.items = ctx.state([])

    def ui(self):
        self.root = Column(padding=16, nodes=[Text("Hello MiniUI")])

if __name__ == "__main__":
    MyApp()
```

- `@run`：创建 `QApplication`、窗口、`UiCanvas`
- `mount`：逻辑层（`ctx.state`、`ctx.animate`、回调）
- `ui`：赋值 `self.root = ...`（`Row` / `Column` 支持 `nodes=[...]` 写法）
- `DerivedText` / `ForEach`：派生文案与列表，见 `demos/state.py`、`demos/demo_app.py`

## Demo 列表（建议按序运行）

| # | 文件 | 主题 |
|---|------|------|
| 01 | `demos/minimal_app.py` | 最小窗口 + 根 `Text` |
| 02 | `demos/button.py` | `Button`、`hit_test`、按下态重绘 |
| 03 | `demos/flex.py` | 主轴 flex：固定宽 + `flex=1` 分剩余 |
| 04 | `demos/padding.py` | `Column` 的 `padding` / `spacing` |
| 05 | `demos/spacer.py` | `Spacer(flex=1)` |
| 06 | `demos/box.py` | `Box` 色块；`label` 过长自动省略号 |
| 07 | `demos/text_input.py` | `TextInput`、焦点、键盘、Enter |
| 08 | `demos/ellipsis.py` | `Text(overflow="ellipsis")` |
| 09 | `demos/scroll.py` | `ScrollView`、滚轮 |
| 10 | `demos/state.py` | `State` + `ForEach` |
| 11 | `demos/animation.py` | `ctx.animate` / `paint_dx` |
| 12 | `demos/theme.py` | `ctx.toggle_theme` |
| 13 | `demos/demo_app.py` | 综合待办（DSL） |
| 14 | `demos/split_column.py` | 两列 `flex=1` 平分；layout vs paint 脏标记 |

```bash
python demos/flex.py
python demos/split_column.py
python demos/demo_app.py
```

## Flex 规则（当前实现）

父 `Row` / `Column` 若存在 `flex > 0` 的子节点：

1. 先 measure **`flex == 0`** 的子节点（可使用 `Box(width=…)` 等固定尺寸），占满主轴固定部分。
2. **剩余主轴** 按 `flex` 比例切成份额；`flex > 0` 的子节点**只在各自份额内** measure，layout 槽位宽度 = 份额（与 intrinsic 无关）。
3. **`flex > 0` 时忽略** 子节点上的 `Box` 固定 `width` / `height`（交叉轴仍可由 `align="stretch"` 拉满）。

因此两列都写 `flex=1` 会始终各占一半；侧栏文案变长应在列内用 `overflow="ellipsis"`，而不是撑宽列。

## 脏标记

| API | 行为 |
|-----|------|
| `mark_layout_dirty()` | 沿 `parent` 链标脏直到根 → 整树 `relayout()` |
| `mark_paint_dirty()` | 仅自身 → 局部 `repaint`（如按钮按下、输入框打字） |

`Text.text = ...` 会 `mark_layout_dirty`；`TextInput.text = ...` 仅 `mark_paint_dirty`。

## 目录

```text
miniui/          # 框架：node, row, column, flex, canvas, widgets, dsl, state, scroll, …
demos/           # 分步 demo
requirements.txt
```
