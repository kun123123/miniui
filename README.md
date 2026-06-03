# MiniUI

PyQt6 自绘 UI 框架。原理见博客：[MiniUI：从零理解渲染树、布局与绘制](https://nimble-cocada-736242.netlify.app/category/gui/miniui-framework/)（本地 `blog/src/content/blog/miniui-framework.md`）。

## 安装

```bash
cd code/ui
pip install -r requirements.txt
```

## 快速开始

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from miniui import Button, Column, Text, UiCanvas


def main() -> None:
    app = QApplication(sys.argv)
    label = Text("Hello MiniUI", font_size=18, bold=True)

    def on_click() -> None:
        label.set_text("已点击")

    canvas = UiCanvas(
        Column(
            padding=20,
            spacing=12,
            children=[label, Button("点我", on_click=on_click)],
        )
    )

    window = QMainWindow()
    central = QWidget()
    lay = QVBoxLayout(central)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(canvas)
    window.setCentralWidget(central)
    window.resize(360, 200)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

组件 API 与用法说明见 **[docs/README.md](docs/README.md)**。

## 目录

```text
miniui/       框架核心
docs/         原理笔记，见 docs/README.md
```

## License

MIT
