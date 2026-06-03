# Step 12～15：Todo、输入框、局部重绘、IME

## Step 12 · 综合 Todo

串联：侧栏、`ScrollView` 列表、`TextInput` + 按钮、`hit_test`、动态 `add_child`。

### 常见坑

勾选待办时在文案前加 `✓ `，字符串变长，必须：

```python
text.set_text(prefix + label)
canvas.relayout()
canvas.repaint()
```

否则 `Text.rect` 不变，末尾文字会被右侧 `×` 按钮盖住。

Todo 文案建议 `Text(..., flex=1)`，中间列占满行宽。

---

## Step 13 · TextInput（英文路径）

### 分层

| 层 | 职责 |
|----|------|
| `UiCanvas` | `_focused_input`、`setFocus()`、`keyPressEvent`、光标 Timer |
| `TextInput` | `text` / `cursor`、`handle_key`、`paint` 自绘 |

流程：点击 → `_set_focus` → 按键 → `handle_key` → `insert` → `repaint_node`。

光标闪烁：`QTimer` 切换 `_cursor_visible`，`paint` 里 `drawLine`。

---

## Step 14 · 局部重绘

### Step 8 vs Step 14

| | Step 8 | Step 14 |
|--|--------|---------|
| `repaint_node` | 限定 Qt 脏矩形 | 同左 |
| `paintEvent` | 仍整树 `paint` | `paint_region` 只画 dirty 子树 |

### 流程

```text
repaint_node → mark_paint_dirty + Qt.repaint(区域)
paintEvent → fillRect(脏区, 背景色)
          → root.paint_region(脏区)
          → 仅 dirty 且相交的叶子 paint()
```

### 文字变长

`repaint_node` 若发现 `layout_dirty`，会先 `relayout`，并重绘新旧 rect **并集**（`Rect.union`）。

---

## Step 15 · IME 中文输入

### 两条通道

| 通道 | API | 用途 |
|------|-----|------|
| 英文/功能键 | `keyPressEvent` → `handle_key` | 直接 insert |
| 中文 IME | `inputMethodEvent` → `handle_input_method` | 预编辑 + 上屏 |

### 状态

- `text`：已确认内容
- `composition`：预编辑（`preeditString()`），paint 带下划线

### Canvas

- `WA_InputMethodEnabled`
- `inputMethodQuery(ImCursorRectangle)` → 候选窗定位
- 失焦时 `clear_composition()`

### 自测

- `step15_ime.py`：微软拼音打拼音 → 下划线 → 选词上屏
- `step12_todo.py`：中文添加待办
