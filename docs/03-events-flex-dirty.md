# Step 6～8：事件、flex、脏标记

## Step 6 · 点击与状态

### 核心思路

MiniUI 没有 Qt 的 `clicked` 信号。交互分三层：

```text
mousePress / mouseRelease（UiCanvas）
  → hit_test(x, y)  从根递归，返回最深层命中节点
  → 改状态（如 Button._pressed = True）
  → repaint_node / update  触发重绘
```

| 组件 | 职责 |
|------|------|
| `Node.hit_test` | 默认：`rect.contains` 则返回自己 |
| `Column` / `Row` | 逆序问孩子，返回最上层命中 |
| `Button` | `_pressed` 驱动 paint 颜色 |
| `UiCanvas` | 统一收鼠标，转发业务 `on_click` |

### 自测

- 运行 `step6_events.py`，按下按钮时背景变深
- 改 `on_click` 回调，确认只改 Python 逻辑、不改 layout

---

## Step 7 · flex 与 margin

### flex 是什么

父 `Row` / `Column` 在 **layout** 时，把主轴剩余空间按 `flex` 比例分给子节点。

```python
Row(children=[
    Text("固定"),
    TextInput(flex=1),   # 吃掉剩余宽度
    Button("确定"),
])
```

实现见 `miniui/flex.py`：

1. 先 measure 非 flex 子节点
2. 用剩余空间 measure flex 子节点
3. `apply_flex` 分配主轴尺寸

### Spacer

`Spacer(flex=1)` 只参与布局、不绘制，等价 Flutter `Spacer` / Qt `stretch`。

### margin

`Node.margin` 在 `_measure_with_margin` / `_layout_with_margin` 中处理，相当于 widget 外圈留白。

### 自测

- `step7_flex.py`：中间区域应随窗口变宽

---

## Step 8 · layout_dirty 与 paint_dirty

两类「脏」：

| 标记 | 含义 | 典型触发 | 处理 |
|------|------|----------|------|
| `layout_dirty` | 尺寸/结构可能变 | `set_text`、增删 child、resize | `relayout()` → measure + layout |
| `paint_dirty` | 仅外观变 | 按钮按下、打字 | `repaint_node()` |

`mark_layout_dirty()` 会**向上冒泡**到根；`relayout()` 若根未脏则**直接跳过**（见 demo 计数器）。

`repaint_node` 只 `update(rect)`，不跑 layout。Step 14 才让 `paint_dirty` 参与剪枝绘制。

### 注意

改 `Text.text` 直接赋值**不会**触发布局；应使用 `set_text()`。

### 自测

- `step8_dirty.py`：连按「刷新统计」→ `relayout` 不增，`paint` 增
