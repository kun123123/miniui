# MiniUI

用 **PyQt6 自绘** 实现的最小 UI 教学框架，帮助理解：

```text
UI 代码  →  渲染树  →  measure / layout  →  paint
```

## 快速开始

```bash
git clone https://github.com/kun123123/miniui.git
cd miniui
pip install -r requirements.txt

python demos/step1_paint.py
python demos/step2_tree.py
python demos/step3_column.py
python demos/step4_row.py
python demos/step5_app.py
```

## 五步 demo

| Step | 文件 | 学到什么 |
|------|------|----------|
| 1 | `demos/step1_paint.py` | `QPainter` + 手写矩形 |
| 2 | `demos/step2_tree.py` | 渲染树、递归 `paint` → 见 `docs/02-概念.md` |
| 3 | `demos/step3_column.py` | `Column` 自动算 `spacing` / `padding` |
| 4 | `demos/step4_row.py` | `Row` + 嵌套 |
| 5 | `demos/step5_app.py` | 完整 `measure → layout → paint` |

自测：在 `step3_column.py` 把 `spacing=12` 改成 `24`，子块间距应变大，无需改 y 坐标。

## 目录结构

```text
miniui/       # geometry, node, widgets, column, row, canvas
demos/        # step1～step5
docs/         # 补充说明
```

## 原理文章

配套长文（原理对照表 + Qt 对比）见博客：[MiniUI：从零理解渲染树、布局与绘制](https://nimble-cocada-736242.netlify.app/category/gui/miniui-framework/)

## 与 Qt / Flutter 对照

| MiniUI | Qt | Flutter |
|--------|-----|---------|
| `measure` | `sizeHint()` | constraints → size |
| `layout` | `QLayout::setGeometry` | `performLayout` |
| `paint` | `paintEvent` | `paint` |

## License

MIT
