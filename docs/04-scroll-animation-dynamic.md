# Step 9～11：动画、动态树、滚动

## Step 9 · 动画不改变 layout

### 分离原则

| 属性 | 用途 |
|------|------|
| `rect` | layout 分配的槽位，hit_test 用 |
| `paint_dx` / `paint_dy` | 仅绘制偏移，动画用 |

```python
canvas.animate_offset(node, dx=(0, 40), duration=350)
```

`QPropertyAnimation` 改 `paint_dx`，**不** `relayout`。绘制用 `paint_rect = rect + offset`。

---

## Step 10 · 动态增删子节点

```python
column.add_child(node)    # 内部 mark_layout_dirty
column.remove_child(node)
canvas.relayout()
```

结构变化必须 relayout；可配合 Step 9 做入场/离场动画。

---

## Step 11 · ScrollView

### 两个高度

| 名称 | 含义 |
|------|------|
| `_content_height` | 子树真实高度（measure 时用极大 constraints 量出） |
| `rect.height` | 视口高度（屏幕上可见区域） |

### 绘制

```python
painter.setClipRect(视口)
painter.translate(0, -scroll_y)
child.paint(painter)
```

### 点击

layout 的 `rect` 不变；`hit_test` 用 `y + scroll_y` 转到内容坐标。

### 滚轮

`scroll_by(dy)` → `mark_paint_dirty` → `repaint_node(scroll)`（Step 14 后局部重绘视口）。

### 自测

- `step11_scroll.py`：滚到底仍可点击最后一项按钮
