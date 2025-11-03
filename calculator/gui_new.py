# calculator/gui_new.py - clean GUI implementation

import sys
import math
import numpy as np
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
    QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator

from . import core
from . import graphing


class CalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(900, 650)
        self.current_number = "0"
        self.operation = None
        self.last_number = None
        self.should_reset = False
        self.history = []
        try:
            self.graph_calc = graphing.GraphingCalculator()
        except Exception:
            # calculator/gui_new.py - clean GUI implementation

            import sys
            import math
            import numpy as np
            from pathlib import Path

            from PyQt5.QtWidgets import (
                QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
                QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
                QHBoxLayout, QScrollArea
            )
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont, QDoubleValidator

            from . import core
            from . import graphing


            class CalculatorGUI(QMainWindow):
                def __init__(self):
                    super().__init__()
                    self.setWindowTitle("Calculator")
                    self.setFixedSize(900, 650)
                    self.current_number = "0"
                    self.operation = None
                    self.last_number = None
                    self.should_reset = False
                    self.history = []
                    try:
                        self.graph_calc = graphing.GraphingCalculator()
                    except Exception:
                        self.graph_calc = None
                    self._build_ui()

                def _build_ui(self):
                    container = QWidget()
                    self.setCentralWidget(container)
                    layout = QVBoxLayout(container)
                    self.tabs = QTabWidget()
                    layout.addWidget(self.tabs)
                    # Calc tab
                    calc = QWidget()
                    v = QVBoxLayout(calc)
                    self.display = QLabel(self.current_number)
                    self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.display.setFont(QFont('Monospace', 28))
                    v.addWidget(self.display)
                    grid = QGridLayout()
                    buttons = ['7','8','9','÷','4','5','6','×','1','2','3','-','0','.','=','+']
                    pos = [(r,c) for r in range(4) for c in range(4)]
                    for (r,c), txt in zip(pos, buttons):
                        btn = QPushButton(txt)
                        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        btn.clicked.connect(lambda _, t=txt: self.on_button(t))
                        grid.addWidget(btn, r, c)
                    v.addLayout(grid)
                    self.tabs.addTab(calc, 'Calc')
                    # Graph tab
                    graph = QWidget()
                    gv = QVBoxLayout(graph)
                    fh = QHBoxLayout()
                    self.func_input = QLineEdit()
                    self.func_input.setPlaceholderText('Enter function, e.g. x**2')
                    plot_btn = QPushButton('Plot')
                    plot_btn.clicked.connect(self.on_plot)
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
                    # History
                    hist = QWidget()
                    hv = QVBoxLayout(hist)
                    self.history_area = QScrollArea()
                    self.history_area.setWidgetResizable(True)
                    content = QWidget()
                    self.history_list = QVBoxLayout(content)
                    self.history_area.setWidget(content)
                    hv.addWidget(self.history_area)
                    clear_btn = QPushButton('Clear History')
                    clear_btn.clicked.connect(self.clear_history)
                    hv.addWidget(clear_btn)
                    self.tabs.addTab(hist, 'History')

                def on_button(self, t):
                    if t.isdigit():
                        if self.should_reset:
                            self.current_number = t
                            self.should_reset = False
                        else:
                            self.current_number = ('' if self.current_number=='0' else self.current_number) + t
                    elif t == '.':
                        if '.' not in self.current_number:
                            self.current_number += '.'
                    elif t in ('+', '-', '×', '÷'):
                        try:
                            self.last_number = float(self.current_number)
                        except Exception:
                            self.last_number = 0.0
                        self.operation = t
                        self.should_reset = True
                    elif t == '=':
                        self._compute()
                    self.display.setText(self.current_number)

                def _compute(self):
                    if self.operation is None or self.last_number is None:
                        return
                    try:
                        cur = float(self.current_number)
                        if self.operation == '+':
                            res = core.safe_add(self.last_number, cur)
                        elif self.operation == '-':
                            res = core.safe_sub(self.last_number, cur)
                        elif self.operation == '×':
                            res = core.safe_mul(self.last_number, cur)
                        elif self.operation == '÷':
                            res = core.safe_div(self.last_number, cur)
                        else:
                            res = cur
                        out = core.format_result(res)
                        self.history.insert(0, (f"{self.last_number} {self.operation} {cur}", out))
                        if len(self.history) > 200:
                            self.history = self.history[:200]
                        self.update_history_display()
                        self.current_number = out
                    except Exception:
                        self.current_number = 'Error'
                    finally:
                        self.operation = None
                        self.last_number = None
                        self.should_reset = True

                def update_history_display(self):
                    while self.history_list.count():
                        item = self.history_list.takeAt(0)
                        w = item.widget()
                        if w:
                            w.deleteLater()
                    for expr, res in self.history:
                        row = QWidget()
                        h = QHBoxLayout(row)
                        lbl = QLabel(f"{expr} = {res}")
                        btn = QPushButton('Recall')
                        btn.clicked.connect(lambda _, v=res: self.recall(v))
                        h.addWidget(lbl)
                        h.addWidget(btn)
                        self.history_list.addWidget(row)
                    self.history_list.addStretch()

                def recall(self, v):
                    self.current_number = v
                    self.tabs.setCurrentIndex(0)
                    self.display.setText(self.current_number)

                def clear_history(self):
                    self.history = []
                    self.update_history_display()

                def on_plot(self):
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
                w = CalculatorGUI()
                w.show()
                return app.exec_()


            if __name__ == '__main__':
                sys.exit(run_app())
