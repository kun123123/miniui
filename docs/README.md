# MiniUI 文档索引

**分步 demo** → [demos/README.md](../demos/README.md)

## 原理笔记 ↔ Demo

| 文档 | 对应 demo（部分） |
|------|-------------------|
| [02-概念.md](./02-概念.md) | `minimal_app.py` · 渲染树与三遍 pass |
| [03-events-flex-dirty.md](./03-events-flex-dirty.md) | `button.py` · `flex.py` · `padding.py` · `spacer.py` |
| [04-scroll-animation-dynamic.md](./04-scroll-animation-dynamic.md) | `scroll.py` · `animation.py` · `state.py` |
| [05-input-paint-ime.md](./05-input-paint-ime.md) | `text_input.py` · 局部重绘（框架层） |

综合串联 → `demo_app.py`；换肤与省略号 → `theme.py` · `ellipsis.py`。

## 原理笔记

| 主题 | 文档 |
|------|------|
| 渲染树、Rect、Node | [02-概念.md](./02-概念.md) |
| 点击、flex、脏标记 | [03-events-flex-dirty.md](./03-events-flex-dirty.md) |
| 动画、ScrollView | [04-scroll-animation-dynamic.md](./04-scroll-animation-dynamic.md) |
| TextInput、局部重绘、IME | [05-input-paint-ime.md](./05-input-paint-ime.md) |

博客长文：[MiniUI：从零理解渲染树、布局与绘制](https://nimble-cocada-736242.netlify.app/category/gui/miniui-framework/)  
本地：`blog/src/content/blog/miniui-framework.md`
