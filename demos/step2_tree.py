"""
Step 2：渲染树（rect 仍手写）

Step 1 在 paintEvent 里直接画矩形；Step 2 把每块 UI 变成「节点对象」，
挂到树上，再递归 paint。

────────────────────────────────────────────────────────
先搞懂下面 4 个 import（对应 Step 1 里的什么）
────────────────────────────────────────────────────────

  Rect          矩形：x, y, width, height
                Step 1 写 (24, 88, 432, 120) → Step 2 写 Rect(32, 80, 400, 100)

  Node          所有 UI 块的基类（树里的一个结点）
                每个节点都有 rect，以及 layout() / paint() 方法

  Text          一种 Node：在 rect 里画一行字
  Box           一种 Node：在 rect 里画彩色块

────────────────────────────────────────────────────────
本 step 仍没有自动布局！
  title.layout(Rect(32, 32, 400, 28))
  这里的 layout 只是「把这个 rect 存到节点上」，坐标还是你手写。
  自动算 spacing / y 坐标 → 从 Step 3 Column 开始。

运行：python demos/step2_tree.py
"""

import sys
from pathlib import Path

# 让 Python 找到上一级的 miniui 包（code/ui/miniui/）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget

from miniui.geometry import Rect
from miniui.node import Node
from miniui.widgets import Box, Text


# ── 根节点：不画具体内容，只负责遍历 children 并调用它们的 paint ──
class ManualRoot(Node):
    def __init__(self, children: list[Node]) -> None:
        super().__init__()
        self.children = children

    def measure(self, constraints):
        from miniui.geometry import Size

        return Size(constraints.max_width, constraints.max_height)

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def paint(self, painter: QPainter) -> None:
        for child in self.children:
            child.paint(painter)


def _explain_on_startup() -> None:
    print("""
=== Step 2 概念对照 ===

Step 1                          Step 2
──────────────────────────────────────────────────
paintEvent 里写死坐标    →     每个控件是一个 Node 对象
p.drawRoundedRect(24,88…) →     Box(...).layout(Rect(32,80,...))
                                再 root.paint(p) 递归画出来

渲染树（本例）：
  ManualRoot
    ├─ Text  标题
    ├─ Box   绿色内容块
    └─ Text  底部提示

Step 3 开始用 Column 自动算 rect，不用再手写 y=80 这种数字。
""")


class Step2Widget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # ── 1. 创建叶子节点（相当于 Step 1 里「要画的那几块」）──
        title = Text("Step 2 · 渲染树（rect 仍手写）", font_size=16, bold=True)
        body = Box(color="#e8f5e9", label="内容块")
        hint = Text("Step 3 起由 Column 自动算位置", font_size=12)

        # ── 2. 手动指定每块的位置（和 Step 1 一样，只是换成 Rect 对象）──
        # layout() 在本 step 仅表示「保存 rect」，不是自动排版
        title.layout(Rect(32, 32, 400, 28))
        body.layout(Rect(32, 80, 400, 100))
        hint.layout(Rect(32, 200, 200, 20))

        # ── 3. 挂到根上，形成树 ──
        self.root = ManualRoot([title, body, hint])

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#fafafa"))

        # 只调用根节点；它会逐个调用孩子的 paint（递归）
        self.root.paint(p)


def main() -> None:
    _explain_on_startup()
    app = QApplication(sys.argv)
    w = Step2Widget()
    w.resize(480, 300)
    w.setWindowTitle("Step 2 · 树 + 递归 paint")
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
