"""Calculator GUI (clean, single-file implementation).

Compact, self-contained implementation. Keeps UI simple and avoids
large duplicated or corrupted content.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
    QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from . import core
from . import graphing


class CalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(880, 640)
        self.current = "0"
        self.last = None
        self.op = None
        self.should_reset = False
        self.history = []
        try:
            self.graph_calc = graphing.GraphingCalculator()
        except Exception:
            self.graph_calc = None
        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Calc tab
        calc = QWidget()
        v = QVBoxLayout(calc)
        self.display = QLabel(self.current)
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFont(QFont('Monospace', 28))
        v.addWidget(self.display)

        grid = QGridLayout()
        buttons = ['7','8','9','÷','4','5','6','×','1','2','3','-','0','.','=','+']
        pos = [(r, c) for r in range(4) for c in range(4)]
        for (r, c), txt in zip(pos, buttons):
            b = QPushButton(txt)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.clicked.connect(lambda _, t=txt: self._on_button(t))
            grid.addWidget(b, r, c)
        v.addLayout(grid)
        self.tabs.addTab(calc, "Calc")

        # Graph tab
        graph = QWidget()
        gv = QVBoxLayout(graph)
        fh = QHBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText('Enter function, e.g. x**2')
        plot_btn = QPushButton('Plot')
        plot_btn.clicked.connect(self._on_plot)
        fh.addWidget(self.func_input)
        fh.addWidget(plot_btn)
        gv.addLayout(fh)
        try:
            self.canvas = graphing.GraphCanvas(self)
            gv.addWidget(self.canvas)
        except Exception:
            self.canvas = None
            gv.addWidget(QLabel('Graphing unavailable'))
        self.tabs.addTab(graph, 'Graph')

        # History tab
        hist = QWidget()
        hv = QVBoxLayout(hist)
        self.history_area = QScrollArea()
        self.history_area.setWidgetResizable(True)
        content = QWidget()
        self.history_layout = QVBoxLayout(content)
        self.history_area.setWidget(content)
        hv.addWidget(self.history_area)
        clear_btn = QPushButton('Clear History')
        clear_btn.clicked.connect(self._clear_history)
        hv.addWidget(clear_btn)
        self.tabs.addTab(hist, 'History')

    def _on_button(self, txt: str):
        if txt.isdigit():
            if self.should_reset:
                self.current = txt
                self.should_reset = False
            else:
                self.current = ('' if self.current == '0' else self.current) + txt
        elif txt == '.':
            if '.' not in self.current:
                self.current += '.'
        elif txt in ('+', '-', '×', '÷'):
            try:
                self.last = float(self.current)
            except Exception:
                self.last = 0.0
            self.op = txt
            self.should_reset = True
        elif txt == '=':
            self._compute()
        self.display.setText(self.current)

    def _compute(self):
        if self.op is None or self.last is None:
            return
        try:
            cur = float(self.current)
            if self.op == '+':
                res = core.safe_add(self.last, cur)
            elif self.op == '-':
                res = core.safe_sub(self.last, cur)
            elif self.op == '×':
                res = core.safe_mul(self.last, cur)
            elif self.op == '÷':
                res = core.safe_div(self.last, cur)
            else:
                res = cur
            out = core.format_result(res)
            self.history.insert(0, (f"{self.last} {self.op} {cur}", out))
            if len(self.history) > 200:
                self.history = self.history[:200]
            self._refresh_history()
            self.current = out
        except Exception:
            self.current = 'Error'
        finally:
            self.op = None
            self.last = None
            self.should_reset = True

    def _refresh_history(self):
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for expr, res in self.history:
            row = QWidget()
            h = QHBoxLayout(row)
            lbl = QLabel(f"{expr} = {res}")
            btn = QPushButton('Recall')
            btn.clicked.connect(lambda _, v=res: self._recall(v))
            h.addWidget(lbl)
            h.addWidget(btn)
            self.history_layout.addWidget(row)
        self.history_layout.addStretch()

    def _recall(self, v: str):
        self.current = v
        self.tabs.setCurrentIndex(0)
        self.display.setText(self.current)

    def _clear_history(self):
        self.history = []
        self._refresh_history()

    def _on_plot(self):
        expr = self.func_input.text().strip()
        if not expr or not self.canvas:
            return
        try:
            if self.graph_calc:
                self.graph_calc.add_function(expr)
            self.canvas.plot_function(expr)
        except Exception:
            pass


def run_app():
    app = QApplication(sys.argv)
    win = CalculatorGUI()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(run_app())

