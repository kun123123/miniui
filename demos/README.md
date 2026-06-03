# MiniUI 组件参考

最小可运行示例在本目录，每个文件只演示一个主题。建议先跑 `minimal_app.py`，再按需看其它文件。

```bash
cd code/ui
pip install -r requirements.txt
python demos/minimal_app.py
```

## 示例文件

| 文件 | 内容 |
|------|------|
| `minimal_app.py` | 最小应用骨架 + 按钮回调 |
| `layout.py` | Column / Row / Spacer / flex |
| `widgets.py` | Text / Box / Button / TextInput / Theme |
| `scroll.py` | ScrollView 长列表 |
| `state_with.py` | State + Bindings + `with` 块 |
| `animation.py` | `animate_offset` 动画 |
| `demo_app.py` | **综合演示**（TaskHub：侧栏/搜索/滚动/动画/主题） |
| `gallery.py` | **卡片画廊**（动态增删、滑入滑出动画、滚动列表） |

综合验证推荐：

```bash
python demos/demo_app.py
python demos/gallery.py
```

---

## 1. 应用骨架

每个应用固定三步：**建树 → 包进 UiCanvas → 挂到 QMainWindow**。

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from miniui import Column, Text, UiCanvas

app = QApplication(sys.argv)

canvas = UiCanvas(Column(padding=16, children=[Text("Hello", font_size=18)]))

window = QMainWindow()
central = QWidget()
lay = QVBoxLayout(central)
lay.setContentsMargins(0, 0, 0, 0)
lay.addWidget(canvas)
window.setCentralWidget(central)
window.resize(400, 300)
window.show()
sys.exit(app.exec())
```

**最佳实践**

- `QVBoxLayout` 的 margin 设为 0，边距交给 MiniUI 的 `padding`
- 首帧前调用 `canvas.relayout(force=True)`（动态改 `canvas.root` 或 ScrollView 内容时尤其需要）
- 把 `sys.path` 指到 `code/ui` 父目录，或安装为包后再 import

---

## 2. UiCanvas

画布 = PyQt `QWidget` + 布局/绘制调度。

| 方法 | 何时用 |
|------|--------|
| `relayout()` | 结构或尺寸可能变了（增删子节点、`set_text` 改长度） |
| `repaint()` | 整窗同步重绘（刷新列表、换主题后兜底） |
| `repaint_node(node)` | 只更新单个控件（改文字、按钮态、统计数字） |
| `invalidate()` | `relayout()` + 异步 `update()` |
| `set_theme(theme)` | 换肤，不 relayout |
| `animate_offset(node, dx=…, dy=…)` | 动画，**不** relayout |
| `_set_focus(text_input)` | 聚焦输入框（框架内部 API，demo 可用） |

**最佳实践**

```python
# 改列表结构：先 relayout 再整窗 repaint
canvas.relayout()
canvas.repaint()

# 只改外观（勾选、计数）：优先局部
node.mark_paint_dirty()
canvas.repaint_node(node)

# 动画：不要 relayout，用 paint_dx/dy
canvas.animate_offset(row, dy=(0.0, -10.0), duration=120)
```

---

## 3. Column / Row

容器，负责 measure → layout → 排列子节点。

```python
Column(
    padding=16,      # 内边距
    spacing=10,      # 子项间距
    align="start",   # start | center | stretch
    flex=0,          # 在父容器主轴上占剩余空间的比例
    children=[...],
)

Row(spacing=8, align="center", children=[...])
```

**动态增删**

```python
col.add_child(node)      # 自动 mark_layout_dirty
col.remove_child(node)
```

**`with` 块（推荐）**

```python
root = Column(padding=16, spacing=10)
with root:
    Text("标题", font_size=18)
    with Row(spacing=8):
        Button("A")
        Button("B")
```

块内**新创建**的节点（`Text(...)`、`Button(...)`）会自动 `add_child`。

**注意**：块里只写已有变量（如 `scroll`、`draft`）**不会**挂载，必须用 `children=[scroll, draft, ...]` 或 `add_child()`。

---

## 4. Spacer / flex

```python
Row(children=[
    Text("左"),
    Spacer(flex=1),          # 吃掉剩余宽度，不绘制
    Text("右"),
])

Row(flex=1, children=[
    Box(width=80, height=40),
    Box(flex=1, height=40),  # 与 siblings 按比例分剩余空间
])
```

**最佳实践**

- 需要「顶到右侧」用 `Spacer(flex=1)`，不要手算坐标
- 可滚动列表外层 Column 里：`ScrollView(..., flex=1)` 占满中间区域
- `margin` 加在单个节点上，与容器 `padding` 分开

---

## 5. Text

```python
Text("标题", font_size=18, bold=True)
Text("长文本…", flex=1, overflow="ellipsis")  # 超出省略号
```

| 方法 | 说明 |
|------|------|
| `set_text(s)` | 改文案，会 `mark_layout_dirty` |

改完后 `canvas.repaint_node(text)` 或交给 `Bindings.text`。

---

## 6. Box

色块 / 占位，调试布局或做色条。

```python
Box(width=80, height=40, color="#e3f2fd", label="标签", radius=8)
Box(flex=1, height=48)  # 高度固定、宽度拉伸
```

---

## 7. Button

```python
Button("确定", on_click=handler, min_width=72, height=32)
```

- 点击由 `UiCanvas` 处理：`mousePress` 设 `_pressed`，`mouseRelease` 调 `on_click`
- 改 `label` 后需 `mark_paint_dirty()` + `repaint_node(btn)`

---

## 8. TextInput

```python
inp = TextInput("", placeholder="请输入…", flex=1, min_width=120)
inp.on_submit = lambda: print(inp.text)
canvas._set_focus(inp)   # 显示光标、接收键盘/IME
```

- 聚焦：`canvas._set_focus(inp)`；失焦：点其它区域自动 `_set_focus(None)`
- 改 `inp.text` 后 `mark_paint_dirty()` + `repaint_node(inp)`
- 支持中文 IME（框架已接 `inputMethodEvent`）

---

## 9. ScrollView

```python
list_col = Column(spacing=6, padding=4)
# …往 list_col 加子项…
scroll = ScrollView(list_col, flex=1)
```

- **滚轮**：框架自动处理，不要手写 `wheelEvent`
- **内容高于视口**：子 Column 可任意高，视口高度由 flex 决定
- **改列表**：`add_child` / `remove_child` → `relayout()` → `repaint()`

```python
list_col.add_child(new_row)
canvas.relayout()
canvas.repaint()
```

**最佳实践**

- 列表与搜索栏/底栏是兄弟节点，不要 `repaint_node` 整个外层 Column（会误擦兄弟区域）
- ScrollView 内单行更新走 `repaint_node` 时，框架会把 damage 收敛到视口

---

## 10. Theme

```python
from miniui import Theme, UiCanvas

canvas = UiCanvas(root, theme=Theme.light())
canvas.set_theme(Theme.dark())   # 运行时换肤，mark 全树 dirty + update
```

自定义主题：复制 `Theme.light()` 改 `ThemeColors` 字段。

---

## 11. State + Bindings

```python
from miniui import State, Bindings

items = State([...])
bindings = Bindings(canvas)

# 文字跟随 State
bindings.text(label, lambda: f"共 {len(items.value)} 项", items)

# 列表跟随 State
bindings.list(
    list_col,
    lambda: items.value,
    build_row,       # item -> Node
    items,
    scroll=scroll,   # 可选，刷新后 scroll_y 归零
)
```

**最佳实践**

```python
items.value.append(x)
items.update()          # 原地改 list 必须 update()
# 或
items.set(new_list)     # 整体替换
```

`Bindings.list` 内部已 `relayout()` + `repaint()`，无需再手写。

---

## 12. 动画

```python
SLIDE = 100.0

# 滑入
row.paint_dx = -SLIDE
canvas.animate_offset(row, dx=(-SLIDE, 0.0), duration=300)

# 弹跳
canvas.animate_offset(row, dy=(0.0, -10.0), duration=120,
    on_finished=lambda: canvas.animate_offset(row, dy=(-10.0, 0.0), duration=160))

# 滑出后删数据
canvas.animate_offset(row, dx=(row.paint_dx, -SLIDE), duration=280, on_finished=on_removed)
```

- 动画只改 `paint_dx` / `paint_dy`，**layout 槽位不变**
- 动画结束若偏移应归零：`row.reset_paint_offset()`
- 动画期间不要 `relayout()` 同一 subtree

---

## 13. 重绘决策（最佳实践）

| 场景 | 做法 |
|------|------|
| 增删列表项、筛选、窗口 resize | `relayout()` + `repaint()` |
| 改 Text / 按钮文案 / 统计 | `set_text` / `mark_paint_dirty` + `repaint_node` |
| 换主题 | `set_theme()` |
| 勾选、轻弹、滑出 | `animate_offset`，局部自动重绘 |
| 滚动 | 框架 `_repaint_scroll`，无需应用层处理 |
| Row 内多个控件一起更新 | 全部 `mark_paint_dirty()` 后 `repaint_node(row)` |

**避免**

- `update()` 与 `repaint_node` 混用同一帧刷新复杂 UI（易竞态）
- 在 ScrollView 内对单行做全窗 `repaint()`（能用动画或 `repaint_node` 就别全窗）
- 动画进行中 `refresh_list()` 打断 `paint_dx/dy`

---

## 14. 目录与扩展

```
miniui/          框架源码
demos/           本参考 + 最小示例
docs/            原理笔记（可选阅读）
```

扩展自定义控件：继承 `Node`，实现 `measure` / `layout` / `paint` 三方法，挂到 `Column` / `Row` 即可。

原理说明见仓库 [README.md](../README.md) 与博客 MiniUI 系列。
