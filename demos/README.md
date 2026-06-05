# MiniUI Demos

分步示例 + 旗舰应用。**单点 demo 每关只演示一个功能**；学完可跑 `notes_app.py` 看完整产品形态。默认主题 `Theme.dark()`。

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
| 13 | [demo_app.py](./demo_app.py) | 综合待办（DSL + ForEach） |
| 14 | [split_column.py](./split_column.py) | 两列 flex 平分 |
| 15 | [image.py](./image.py) | Image fit 模式 |
| 16 | [text_area.py](./text_area.py) | TextArea 多行输入 |
| ★ | **[notes_app.py](./notes_app.py)** | **MiniNotes 三栏笔记（旗舰）** |

## 运行

```bash
cd code/ui
pip install -r requirements.txt
python demos/minimal_app.py   # 从 01 开始，按表顺序逐个跑
python demos/notes_app.py     # 旗舰：三栏笔记工作台
python demos/demo_app.py      # 综合待办
```

原理长文见博客 [MiniUI：从零理解渲染树、布局与绘制](https://nimble-cocada-736242.netlify.app/category/gui/miniui-framework/)（本地 `blog/src/content/blog/miniui-framework.md`）。
