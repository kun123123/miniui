# MiniUI Demos

13 个分步示例，**每个 demo 只演示一个功能**（最后一关 `demo_app.py` 综合串联）。默认主题 `Theme.dark()`。

| # | 文件 | 主题 |
|---|------|------|
| 01 | [minimal_app.py](./minimal_app.py) | 最小可运行（Qt + UiCanvas + Text） |
| 02 | [button.py](./button.py) | Button 点击 + 属性自动重绘 |
| 03 | [flex.py](./flex.py) | flex 主轴分配 |
| 04 | [padding.py](./padding.py) | padding / spacing |
| 05 | [spacer.py](./spacer.py) | Spacer |
| 06 | [box.py](./box.py) | Box 色块 |
| 07 | [text_input.py](./text_input.py) | TextInput 输入 |
| 08 | [ellipsis.py](./ellipsis.py) | Text 省略号 |
| 09 | [scroll.py](./scroll.py) | ScrollView 滚动 |
| 10 | [state.py](./state.py) | State + Bindings 列表 |
| 11 | [animation.py](./animation.py) | animate_offset |
| 12 | [theme.py](./theme.py) | 换肤 |
| 13 | [demo_app.py](./demo_app.py) | 综合待办（串联以上能力） |

## 运行

```bash
cd code/ui
pip install -r requirements.txt
python demos/minimal_app.py   # 从 01 开始，按表顺序逐个跑
python demos/demo_app.py      # 或直达综合 demo
```

原理长文见博客 [MiniUI：从零理解渲染树、布局与绘制](https://nimble-cocada-736242.netlify.app/category/gui/miniui-framework/)（本地 `blog/src/content/blog/miniui-framework.md`）。
