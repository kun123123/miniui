# MiniUI

PyQt6 自绘 UI 教学框架。原理与细节见博客：[MiniUI：从零理解渲染树、布局与绘制](https://nimble-cocada-736242.netlify.app/category/gui/miniui-framework/)（本地 `blog/src/content/blog/miniui-framework.md`）。

## 安装与运行

```bash
git clone https://github.com/kun123123/miniui.git
cd miniui
pip install -r requirements.txt
```

按顺序运行 demo（建议从头到尾跑一遍）：

```bash
python demos/step1_paint.py
python demos/step2_tree.py
python demos/step3_column.py
python demos/step4_row.py
python demos/step5_app.py
python demos/step6_events.py
python demos/step7_flex.py
python demos/step8_dirty.py
python demos/step9_animation.py
python demos/step10_dynamic.py
python demos/step11_scroll.py
python demos/step12_todo.py
python demos/step13_input.py
python demos/step14_partial_paint.py
python demos/step15_ime.py
python demos/step16_ellipsis.py
python demos/step17_theme.py
python demos/step18_app.py
python demos/step19_ui_with.py
```

## Demo 一览

| 讲什么 | 文件 |
|--------|------|
| 手写坐标 | `demos/step1_paint.py` |
| 渲染树 | `demos/step2_tree.py` |
| 纵向 Column | `demos/step3_column.py` |
| 横向 Row | `demos/step4_row.py` |
| 完整三遍 pass | `demos/step5_app.py` |
| 点击与按钮 | `demos/step6_events.py` |
| flex 剩余空间 | `demos/step7_flex.py` |
| 脏标记 | `demos/step8_dirty.py` |
| 动画偏移 | `demos/step9_animation.py` |
| 动态增删节点 | `demos/step10_dynamic.py` |
| 滚动列表 | `demos/step11_scroll.py` |
| 综合 Todo | `demos/step12_todo.py` |
| 自绘输入框 | `demos/step13_input.py` |
| 局部重绘 | `demos/step14_partial_paint.py` |
| 中文输入法 | `demos/step15_ime.py` |
| 文本省略号 | `demos/step16_ellipsis.py` |
| 浅色 / 深色主题 | `demos/step17_theme.py` |
| 综合应用 TaskHub | `demos/step18_app.py` |
| with 块 + State 响应式 | `demos/step19_ui_with.py` |

## 目录结构

```text
miniui/       # 框架核心
demos/        # 上表 demo
docs/         # 补充笔记，见 docs/README.md
```

## 文档

- [docs/README.md](docs/README.md) — 文档索引

## License

MIT
