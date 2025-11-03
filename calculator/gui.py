"""Thin wrapper re-exporting the clean GUI implementation.

The project historically imported `calculator.gui`. To avoid issues
from the previously corrupted file we provide this small wrapper which
re-exports the implementation from `calculator.gui_new`.
"""

from .gui_new import CalculatorGUI, run_app

__all__ = ["CalculatorGUI", "run_app"]
"""Calculator GUI - clean single-definition file.

This module contains the concrete CalculatorGUI implementation. It was
created as a single, clean replacement to recover from earlier file
corruption in `calculator/gui.py`.
"""

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
        expr = self.func_input.text().strip()
        if expr:
            self.graph_calc.add_function(expr)
            self.graph_canvas.plot_function(expr)

    def clear_plot(self):
        self.graph_calc.clear_functions()
        self.func_input.clear()
        self.graph_canvas.setup_axes()
        self.graph_canvas.draw()

    def update_window(self):
        try:
            values = {name: float(inp.text()) for name, inp in self.window_inputs.items()}
            self.graph_canvas.set_window(**values)
            self.graph_canvas.setup_axes()
            for func in self.graph_calc.get_functions():
                self.graph_canvas.plot_function(func)
        except Exception:
            pass

    def zoom_graph(self, factor):
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            ymin = float(self.window_inputs['ymin'].text())
            ymax = float(self.window_inputs['ymax'].text())

            xcenter = (xmax + xmin) / 2
            ycenter = (ymax + ymin) / 2

            xrange = (xmax - xmin) / factor
            yrange = (ymax - ymin) / factor

            self.window_inputs['xmin'].setText(f"{xcenter - xrange/2:.2f}")
            self.window_inputs['xmax'].setText(f"{xcenter + xrange/2:.2f}")
            self.window_inputs['ymin'].setText(f"{ycenter - yrange/2:.2f}")
            self.window_inputs['ymax'].setText(f"{ycenter - yrange/2:.2f}")

            self.update_window()
        except Exception:
            pass

    def reset_graph_view(self):
        self.window_inputs['xmin'].setText("-10")
        self.window_inputs['xmax'].setText("10")
        self.window_inputs['ymin'].setText("-10")
        self.window_inputs['ymax'].setText("10")
        self.window_inputs['xscl'].setText("1")
        self.window_inputs['yscl'].setText("1")
        self.update_window()

    def trace_point(self):
        try:
            x = float(self.trace_x.text())
            expr = self.func_input.text().strip()

            if expr:
                y = self.graph_canvas.trace_function(expr, x)
                if y is not None:
                    self.graph_canvas.plot_point(x, y)
                    self.analysis_result.setText(f"Point: ({x:.3f}, {y:.3f})")
                else:
                    self.analysis_result.setText("Could not evaluate function at this point")
        except ValueError:
            self.analysis_result.setText("Invalid x value")

    def find_zeros(self):
        expr = self.func_input.text().strip()
        if not expr:
            return
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            zeros = self.graph_calc.find_zeros(expr, xmin, xmax)

            if zeros:
                for x in zeros:
                    self.graph_canvas.plot_point(x, 0, color='green')
                zeros_str = ", ".join(f"x = {x:.3f}" for x in zeros)
                self.analysis_result.setText(f"Zeros found: {zeros_str}")
            else:
                self.analysis_result.setText("No zeros found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding zeros: {str(e)}")

    def find_intersections(self):
        try:
            expr1 = self.func_input.text().strip()
            if not expr1:
                self.analysis_result.setText("Enter first function")
                return
            expr2, ok = QInputDialog.getText(self, "Find Intersections", "Enter second function:")
            if ok and expr2:
                xmin = float(self.window_inputs['xmin'].text())
                xmax = float(self.window_inputs['xmax'].text())
                points = self.graph_calc.find_intersections(expr1, expr2, xmin, xmax)
                if points:
                    for x, y in points:
                        self.graph_canvas.plot_point(x, y, color='blue')
                    points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                    self.analysis_result.setText(f"Intersections: {points_str}")
                else:
                    self.analysis_result.setText("No intersections found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding intersections: {str(e)}")

    def find_critical_points(self):
        expr = self.func_input.text().strip()
        if not expr:
            return
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            points = self.graph_calc.find_critical_points(expr, xmin, xmax)
            if points:
                for x, y in points:
                    self.graph_canvas.plot_point(x, y, color='purple')
                points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                self.analysis_result.setText(f"Critical points: {points_str}")
            else:
                self.analysis_result.setText("No critical points found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding critical points: {str(e)}")

    # ---------- History tab ----------
    def setup_history_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.history_list = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)

        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_content.setStyleSheet("background-color: rgba(0,0,0,0.03); border-radius: 5px; padding: 10px;")

        self.history_layout.addWidget(scroll)

        controls = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        controls.addWidget(clear_btn)
        controls.addStretch()
        self.history_layout.addLayout(controls)

        self.update_history_display()

    def clear_history(self):
        self.history = []
        self.update_history_display()

    def recall_history(self, value):
        self.current_number = value
        self.update_display()
        self.tabs.setCurrentIndex(0)

    def update_history_display(self):
        while self.history_list.count():
            item = self.history_list.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for expr, result in self.history:
            row = QWidget()
            layout = QHBoxLayout(row)
            label = QLabel(f"{expr} = {result}")
            label.setWordWrap(True)
            recall = QPushButton("Recall")
            recall.setMaximumWidth(80)
            recall.clicked.connect(lambda _, v=result: self.recall_history(v))
            layout.addWidget(label)
            layout.addWidget(recall)
            self.history_list.addWidget(row)
        self.history_list.addStretch()

    def set_styles(self):
        self.current_theme = 'dark'
        self.apply_theme()

    def apply_theme(self):
        try:
            theme_file = Path(__file__).parent / 'styles' / 'themes' / f'{self.current_theme}.qss'
            if theme_file.exists():
                self.setStyleSheet(theme_file.read_text())
                if self.current_theme == 'dark':
                    self.theme_btn.setText("☀️ Light Mode")
                else:
                    self.theme_btn.setText("🌙 Dark Mode")
        except Exception:
            self.setStyleSheet('QWidget { background: #2b3136 }')

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()


def run_app():
    app = QApplication(sys.argv)
    w = CalculatorGUI()
    w.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(run_app())
"""
GUI for the calculator. Uses PyQt5. Keeps UI concerns separate from core logic.
This module provides a CalculatorGUI class with Basic, Scientific, Graph and History tabs.
"""
import sys
import math
import numpy as np
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
    QHBoxLayout, QGroupBox, QFormLayout, QInputDialog, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator

from . import core
from . import graphing


class CalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(800, 640)

        # State
        self.current_number = "0"
        self.operation = None
        self.last_number = None
        self.should_reset = False
        self.memory = 0.0
        self.angle_mode = "DEG"
        self.graph_calc = graphing.GraphingCalculator()

        # History tracking
        self.history = []  # List of (expression, result) tuples

        # Main widget
        self.main_widget = QWidget()
        """
        Calculator GUI (clean single-definition file).

        This file provides the CalculatorGUI class with Basic, Scientific, Graph and History
        tabs. It intentionally contains one coherent implementation to avoid prior merge
        and duplication issues.
        """

        import sys
        import math
        import numpy as np
        from pathlib import Path

        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
            QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
            QHBoxLayout, QGroupBox, QFormLayout, QInputDialog, QScrollArea
        )
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont, QDoubleValidator

        from . import core
        from . import graphing


        class CalculatorGUI(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("Calculator")
                self.setFixedSize(800, 640)

                # State
                self.current_number = "0"
                self.operation = None
                self.last_number = None
                self.should_reset = False
                self.memory = 0.0
                self.angle_mode = "DEG"
                self.graph_calc = graphing.GraphingCalculator()

                # History tracking
                self.history = []  # List of (expression, result) tuples

                # Main widget
                self.main_widget = QWidget()
                self.setCentralWidget(self.main_widget)
                main_layout = QVBoxLayout(self.main_widget)

                # Theme toggle
                theme_layout = QHBoxLayout()
                self.theme_btn = QPushButton("🌙 Dark Mode")
                self.theme_btn.setObjectName("theme-toggle")
                self.theme_btn.clicked.connect(self.toggle_theme)
                theme_layout.addStretch()
                theme_layout.addWidget(self.theme_btn)
                main_layout.addLayout(theme_layout)

                self.tabs = QTabWidget()
                main_layout.addWidget(self.tabs)

                # Basic tab
                self.basic_tab = QWidget()
                self.basic_layout = QVBoxLayout(self.basic_tab)
                self.basic_display = QLabel("0")
                self.basic_display.setObjectName("display")
                self.basic_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.basic_display.setFont(QFont('Monospace', 24))
                self.basic_layout.addWidget(self.basic_display)
                self.create_basic_grid(self.basic_layout)
                self.tabs.addTab(self.basic_tab, "Basic")

                # Scientific tab
                self.scientific_tab = QWidget()
                self.scientific_layout = QVBoxLayout(self.scientific_tab)
                self.scientific_display = QLabel("0")
                self.scientific_display.setObjectName("display")
                self.scientific_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.scientific_display.setFont(QFont('Monospace', 20))
                self.scientific_layout.addWidget(self.scientific_display)
                self.create_scientific_grid(self.scientific_layout)
                self.tabs.addTab(self.scientific_tab, "Scientific")

                # Graphing tab
                self.graphing_page = QWidget()
                self.graphing_layout = QVBoxLayout(self.graphing_page)
                self.setup_graphing_tab()
                self.tabs.addTab(self.graphing_page, "Graph")

                # History tab
                self.history_tab = QWidget()
                self.history_layout = QVBoxLayout(self.history_tab)
                self.setup_history_tab()
                self.tabs.addTab(self.history_tab, "History")

                self.set_styles()

            # ---------- UI builders ----------
            def create_basic_grid(self, parent_layout):
                grid = QGridLayout()
                labels = [
                    ('MC','MR','M+','M-','C'),
                    ('±','√','%','÷','←'),
                    ('7','8','9','×','x²'),
                    ('4','5','6','-','1/x'),
                    ('1','2','3','+','=' )
                ]

                for r, row in enumerate(labels):
                    for c, txt in enumerate(row):
                        btn = self.make_button(txt)
                        grid.addWidget(btn, r, c)

                # last row with 0 spanning two columns
                zero = self.make_button('0')
                grid.addWidget(zero, len(labels), 0, 1, 2)
                grid.addWidget(self.make_button('.'), len(labels), 2)
                grid.addWidget(self.make_button('π'), len(labels), 3)
                grid.addWidget(self.make_button('e'), len(labels), 4)

                parent_layout.addLayout(grid)

            def create_scientific_grid(self, parent_layout):
                grid = QGridLayout()
                layout = [
                    ('DEG','RAD','INV','log','ln'),
                    ('sin','cos','tan','(',')'),
                    ('asin','acos','atan','^','|x|'),
                    ('sinh','cosh','tanh','⌊x⌋','⌈x⌉'),
                    ('nPr','nCr','x!','rand','EE'),
                    ('7','8','9','÷','←'),
                    ('4','5','6','×','C'),
                    ('1','2','3','-','='),
                    ('0','0','.','π','+')
                ]

                for r, row in enumerate(layout):
                    for c, txt in enumerate(row):
                        if txt == '0' and (r, c) != (8, 0):
                            continue
                        if txt == '0':
                            btn = self.make_button('0')
                            grid.addWidget(btn, r, c, 1, 2)
                            continue
                        btn = self.make_button(txt)
                        grid.addWidget(btn, r, c)

                parent_layout.addLayout(grid)

            def make_button(self, text):
                btn = QPushButton(text)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.clicked.connect(lambda checked, t=text: self.button_click(t))
                return btn

            # ---------- event handling ----------
            def button_click(self, value):
                try:
                    # Numeric entry
                    if value.isdigit():
                        if self.should_reset:
                            self.current_number = value
                            self.should_reset = False
                        else:
                            self.current_number = self.current_number if self.current_number != '0' else ''
                            self.current_number += value

                    elif value == '.':
                        if '.' not in self.current_number:
                            self.current_number += '.'

                    elif value in ('π','e'):
                        self.current_number = str(math.pi if value == 'π' else math.e)
                        self.should_reset = True

                    elif value == '←':
                        self.current_number = self.current_number[:-1] if len(self.current_number) > 1 else '0'

                    elif value in ('C',):
                        self.clear()

                    elif value == '±':
                        if self.current_number and self.current_number != '0':
                            if self.current_number.startswith('-'):
                                self.current_number = self.current_number[1:]
                            else:
                                self.current_number = '-' + self.current_number

                    elif value == '%':
                        try:
                            self.current_number = str(float(self.current_number) / 100.0)
                        except Exception:
                            self.current_number = 'Error'

                    elif value in ('+', '-', '×', '÷', '^', 'nPr', 'nCr'):
                        # store operator
                        try:
                            self.last_number = float(self.current_number)
                        except Exception:
                            self.last_number = 0.0
                        self.operation = value
                        self.should_reset = True

                    elif value == '=':
                        self.execute_operation()

                    elif value == 'rand':
                        self.current_number = str(np.random.random())

                    elif value == 'x²':
                        try:
                            v = float(self.current_number)
                            self.current_number = str(v * v)
                        except Exception:
                            self.current_number = 'Error'

                    elif value == '√':
                        try:
                            v = float(self.current_number)
                            self.current_number = str(math.sqrt(v))
                        except Exception:
                            self.current_number = 'Error'

                    elif value == 'x!':
                        try:
                            self.current_number = str(core.factorial(float(self.current_number)))
                        except Exception:
                            self.current_number = 'Error'

                    # update display for both tabs to be consistent (active tab shown)
                    self.update_display()

                except Exception:
                    self.current_number = 'Error'
                    self.update_display()

            def execute_operation(self):
                try:
                    if self.operation is None or self.last_number is None:
                        return
                    cur = float(self.current_number)
                    if self.operation == '+':
                        res = core.safe_add(self.last_number, cur)
                    elif self.operation == '-':
                        res = core.safe_sub(self.last_number, cur)
                    elif self.operation == '×':
                        res = core.safe_mul(self.last_number, cur)
                    elif self.operation == '÷':
                        res = core.safe_div(self.last_number, cur)
                    elif self.operation == '^':
                        res = core.power(self.last_number, cur)
                    elif self.operation == 'nPr':
                        res = core.nPr(self.last_number, cur)
                    elif self.operation == 'nCr':
                        res = core.nCr(self.last_number, cur)
                    else:
                        res = cur

                    # Add operation to history
                    result = core.format_result(res)
                    if not result.startswith('Error'):
                        self.history.insert(0, (f"{self.last_number} {self.operation} {cur}", result))
                        if len(self.history) > 100:
                            self.history = self.history[:100]
                        if hasattr(self, 'history_list'):
                            self.update_history_display()

                    self.current_number = result
                    self.operation = None
                    self.last_number = None
                    self.should_reset = True
                except Exception:
                    self.current_number = 'Error'

            def clear(self):
                self.current_number = '0'
                self.operation = None
                self.last_number = None
                self.should_reset = False

            def update_display(self):
                # update both displays but active tab will be visible
                try:
                    self.basic_display.setText(self.current_number)
                    self.scientific_display.setText(self.current_number)
                except Exception:
                    pass

            # ---------- Graphing ----------
            def setup_graphing_tab(self):
                """Create the graphing interface similar to TI-84"""
                controls = QHBoxLayout()

                # Function input
                func_group = QGroupBox("Y=")
                func_layout = QVBoxLayout()
                self.func_input = QLineEdit()
                self.func_input.setPlaceholderText("Enter function (e.g., x^2)")
                plot_btn = QPushButton("Plot")
                plot_btn.clicked.connect(self.plot_function)
                clear_btn = QPushButton("Clear")
                clear_btn.clicked.connect(self.clear_plot)
                func_layout.addWidget(self.func_input)
                func_layout.addWidget(plot_btn)
                func_layout.addWidget(clear_btn)
                func_group.setLayout(func_layout)
                controls.addWidget(func_group)

                # Window settings
                window_group = QGroupBox("Window")
                window_layout = QFormLayout()
                self.window_inputs = {}
                for name in ['xmin', 'xmax', 'ymin', 'ymax', 'xscl', 'yscl']:
                    inp = QLineEdit()
                    inp.setValidator(QDoubleValidator())
                    self.window_inputs[name] = inp
                    window_layout.addRow(name.capitalize(), inp)

                defaults = {'xmin': '-10', 'xmax': '10', 'ymin': '-10', 'ymax': '10', 'xscl': '1', 'yscl': '1'}
                for name, value in defaults.items():
                    self.window_inputs[name].setText(value)

                update_btn = QPushButton("Update Window")
                update_btn.clicked.connect(self.update_window)
                window_layout.addWidget(update_btn)

                zoom_layout = QHBoxLayout()
                zoom_in = QPushButton("Zoom In (×2)")
                zoom_out = QPushButton("Zoom Out (÷2)")
                zoom_std = QPushButton("Standard")
                zoom_in.clicked.connect(lambda: self.zoom_graph(2))
                zoom_out.clicked.connect(lambda: self.zoom_graph(0.5))
                zoom_std.clicked.connect(self.reset_graph_view)
                zoom_layout.addWidget(zoom_in)
                zoom_layout.addWidget(zoom_out)
                zoom_layout.addWidget(zoom_std)
                window_layout.addRow(zoom_layout)

                window_group.setLayout(window_layout)
                controls.addWidget(window_group)

                # Analysis controls
                analysis_group = QGroupBox("Analysis")
                analysis_layout = QVBoxLayout()

                trace_layout = QHBoxLayout()
                self.trace_x = QLineEdit()
                self.trace_x.setPlaceholderText("X value")
                self.trace_x.setValidator(QDoubleValidator())
                trace_btn = QPushButton("Trace")
                trace_btn.clicked.connect(self.trace_point)
                trace_layout.addWidget(self.trace_x)
                trace_layout.addWidget(trace_btn)
                analysis_layout.addLayout(trace_layout)

                btn_layout = QHBoxLayout()
                zeros_btn = QPushButton("Find Zeros")
                intersect_btn = QPushButton("Intersections")
                critical_btn = QPushButton("Critical Points")
                clear_pts_btn = QPushButton("Clear Points")

                zeros_btn.clicked.connect(self.find_zeros)
                intersect_btn.clicked.connect(self.find_intersections)
                critical_btn.clicked.connect(self.find_critical_points)
                clear_pts_btn.clicked.connect(lambda: self.graph_canvas.clear_points())

                btn_layout.addWidget(zeros_btn)
                btn_layout.addWidget(intersect_btn)
                btn_layout.addWidget(critical_btn)
                btn_layout.addWidget(clear_pts_btn)
                analysis_layout.addLayout(btn_layout)

                self.analysis_result = QLabel("")
                analysis_layout.addWidget(self.analysis_result)

                analysis_group.setLayout(analysis_layout)
                controls.addWidget(analysis_group)

                self.graphing_layout.addLayout(controls)

                # plotting canvas
                self.graph_canvas = graphing.GraphCanvas(self)
                self.graphing_layout.addWidget(self.graph_canvas)

            def plot_function(self):
                """Plot the current function"""
                expr = self.func_input.text().strip()
                if expr:
                    self.graph_calc.add_function(expr)
                    self.graph_canvas.plot_function(expr)

            def clear_plot(self):
                """Clear all plotted functions"""
                self.graph_calc.clear_functions()
                self.func_input.clear()
                self.graph_canvas.setup_axes()
                self.graph_canvas.draw()

            def update_window(self):
                """Update the plotting window ranges"""
                try:
                    values = {name: float(inp.text()) for name, inp in self.window_inputs.items()}
                    self.graph_canvas.set_window(**values)
                    self.graph_canvas.setup_axes()
                    for func in self.graph_calc.get_functions():
                        self.graph_canvas.plot_function(func)
                except Exception:
                    pass

            def zoom_graph(self, factor):
                """Zoom in or out by the given factor"""
                try:
                    xmin = float(self.window_inputs['xmin'].text())
                    xmax = float(self.window_inputs['xmax'].text())
                    ymin = float(self.window_inputs['ymin'].text())
                    ymax = float(self.window_inputs['ymax'].text())

                    xcenter = (xmax + xmin) / 2
                    ycenter = (ymax + ymin) / 2

                    xrange = (xmax - xmin) / factor
                    yrange = (ymax - ymin) / factor

                    self.window_inputs['xmin'].setText(f"{xcenter - xrange/2:.2f}")
                    self.window_inputs['xmax'].setText(f"{xcenter + xrange/2:.2f}")
                    self.window_inputs['ymin'].setText(f"{ycenter - yrange/2:.2f}")
                    self.window_inputs['ymax'].setText(f"{ycenter - yrange/2:.2f}")

                    self.update_window()
                except Exception:
                    pass

            def reset_graph_view(self):
                """Reset to standard window (-10,10) x (-10,10)"""
                self.window_inputs['xmin'].setText("-10")
                self.window_inputs['xmax'].setText("10")
                self.window_inputs['ymin'].setText("-10")
                self.window_inputs['ymax'].setText("10")
                self.window_inputs['xscl'].setText("1")
                self.window_inputs['yscl'].setText("1")
                self.update_window()

            def trace_point(self):
                """Trace a point on the current function"""
                try:
                    x = float(self.trace_x.text())
                    expr = self.func_input.text().strip()

                    if expr:
                        y = self.graph_canvas.trace_function(expr, x)
                        if y is not None:
                            self.graph_canvas.plot_point(x, y)
                            self.analysis_result.setText(f"Point: ({x:.3f}, {y:.3f})")
                        else:
                            self.analysis_result.setText("Could not evaluate function at this point")
                except ValueError:
                    self.analysis_result.setText("Invalid x value")

            def find_zeros(self):
                """Find x-intercepts of the current function"""
                expr = self.func_input.text().strip()
                if not expr:
                    return
                try:
                    xmin = float(self.window_inputs['xmin'].text())
                    xmax = float(self.window_inputs['xmax'].text())
                    zeros = self.graph_calc.find_zeros(expr, xmin, xmax)

                    if zeros:
                        for x in zeros:
                            self.graph_canvas.plot_point(x, 0, color='green')
                        zeros_str = ", ".join(f"x = {x:.3f}" for x in zeros)
                        self.analysis_result.setText(f"Zeros found: {zeros_str}")
                    else:
                        self.analysis_result.setText("No zeros found in current window")
                except Exception as e:
                    self.analysis_result.setText(f"Error finding zeros: {str(e)}")

            def find_intersections(self):
                """Find intersections between two functions"""
                try:
                    expr1 = self.func_input.text().strip()
                    if not expr1:
                        self.analysis_result.setText("Enter first function")
                        return
                    expr2, ok = QInputDialog.getText(self, "Find Intersections", "Enter second function:")
                    if ok and expr2:
                        xmin = float(self.window_inputs['xmin'].text())
                        xmax = float(self.window_inputs['xmax'].text())
                        points = self.graph_calc.find_intersections(expr1, expr2, xmin, xmax)
                        if points:
                            for x, y in points:
                                self.graph_canvas.plot_point(x, y, color='blue')
                            points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                            self.analysis_result.setText(f"Intersections: {points_str}")
                        else:
                            self.analysis_result.setText("No intersections found in current window")
                except Exception as e:
                    self.analysis_result.setText(f"Error finding intersections: {str(e)}")

            def find_critical_points(self):
                """Find local maxima and minima"""
                expr = self.func_input.text().strip()
                if not expr:
                    return
                try:
                    xmin = float(self.window_inputs['xmin'].text())
                    xmax = float(self.window_inputs['xmax'].text())
                    points = self.graph_calc.find_critical_points(expr, xmin, xmax)
                    if points:
                        for x, y in points:
                            self.graph_canvas.plot_point(x, y, color='purple')
                        points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                        self.analysis_result.setText(f"Critical points: {points_str}")
                    else:
                        self.analysis_result.setText("No critical points found in current window")
                except Exception as e:
                    self.analysis_result.setText(f"Error finding critical points: {str(e)}")

            # ---------- History tab ----------
            def setup_history_tab(self):
                """Create the history tab with a list of past calculations"""
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll_content = QWidget()
                self.history_list = QVBoxLayout(scroll_content)
                scroll.setWidget(scroll_content)
                scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
                scroll_content.setStyleSheet("background-color: rgba(0,0,0,0.03); border-radius: 5px; padding: 10px;")
                self.history_layout.addWidget(scroll)
                controls = QHBoxLayout()
                clear_btn = QPushButton("Clear History")
                clear_btn.clicked.connect(self.clear_history)
                controls.addWidget(clear_btn)
                controls.addStretch()
                self.history_layout.addLayout(controls)
                self.update_history_display()

            def clear_history(self):
                """Clear the calculation history"""
                self.history = []
                self.update_history_display()

            def recall_history(self, value):
                """Recall a value from history into the current calculation"""
                self.current_number = value
                self.update_display()
                self.tabs.setCurrentIndex(0)

            def update_history_display(self):
                """Update the history tab display with recent calculations"""
                while self.history_list.count():
                    item = self.history_list.takeAt(0)
                    w = item.widget()
                    if w:
                        w.deleteLater()
                for expr, result in self.history:
                    row = QWidget()
                    layout = QHBoxLayout(row)
                    label = QLabel(f"{expr} = {result}")
                    label.setWordWrap(True)
                    recall = QPushButton("Recall")
                    recall.setMaximumWidth(80)
                    recall.clicked.connect(lambda _, v=result: self.recall_history(v))
                    layout.addWidget(label)
                    layout.addWidget(recall)
                    self.history_list.addWidget(row)
                self.history_list.addStretch()

            def set_styles(self):
                """Initialize with dark theme by default"""
                self.current_theme = 'dark'
                self.apply_theme()

            def apply_theme(self):
                """Apply the current theme"""
                try:
                    theme_file = Path(__file__).parent / 'styles' / 'themes' / f'{self.current_theme}.qss'
                    if theme_file.exists():
                        self.setStyleSheet(theme_file.read_text())
                        if self.current_theme == 'dark':
                            self.theme_btn.setText("☀️ Light Mode")
                        else:
                            self.theme_btn.setText("🌙 Dark Mode")
                except Exception:
                    self.setStyleSheet('QWidget { background: #2b3136 }')

            def toggle_theme(self):
                """Switch between light and dark themes"""
                self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
                self.apply_theme()


        def run_app():
            app = QApplication(sys.argv)
            w = CalculatorGUI()
            w.show()
            return app.exec_()


        if __name__ == '__main__':
            sys.exit(run_app())
        # State
        self.current_number = "0"
        self.operation = None
        self.last_number = None
        self.should_reset = False
        self.memory = 0.0
        self.angle_mode = "DEG"
        self.graph_calc = graphing.GraphingCalculator()

        # History tracking
        self.history = []  # List of (expression, result) tuples

        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        # Theme toggle
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setObjectName("theme-toggle")
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Basic tab
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        self.basic_display = QLabel("0")
        self.basic_display.setObjectName("display")
        self.basic_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.basic_display.setFont(QFont('Monospace', 24))
        self.basic_layout.addWidget(self.basic_display)
        self.create_basic_grid(self.basic_layout)
        self.tabs.addTab(self.basic_tab, "Basic")

        # Scientific tab
        self.scientific_tab = QWidget()
        self.scientific_layout = QVBoxLayout(self.scientific_tab)
        self.scientific_display = QLabel("0")
        self.scientific_display.setObjectName("display")
        self.scientific_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scientific_display.setFont(QFont('Monospace', 20))
        self.scientific_layout.addWidget(self.scientific_display)
        self.create_scientific_grid(self.scientific_layout)
        self.tabs.addTab(self.scientific_tab, "Scientific")

        # Graphing tab
        self.graphing_page = QWidget()
        self.graphing_layout = QVBoxLayout(self.graphing_page)
        self.setup_graphing_tab()
        self.tabs.addTab(self.graphing_page, "Graph")

        # History tab
        self.history_tab = QWidget()
        self.history_layout = QVBoxLayout(self.history_tab)
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, "History")

        self.set_styles()

    # ---------- UI builders ----------
    def create_basic_grid(self, parent_layout):
        grid = QGridLayout()
        labels = [
            ('MC','MR','M+','M-','C'),
            ('±','√','%','÷','←'),
            ('7','8','9','×','x²'),
            ('4','5','6','-','1/x'),
            ('1','2','3','+','=')
        ]

        for r, row in enumerate(labels):
            for c, txt in enumerate(row):
                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        # last row with 0 spanning two columns
        zero = self.make_button('0')
        grid.addWidget(zero, len(labels), 0, 1, 2)
        grid.addWidget(self.make_button('.'), len(labels), 2)
        grid.addWidget(self.make_button('π'), len(labels), 3)
        grid.addWidget(self.make_button('e'), len(labels), 4)

        parent_layout.addLayout(grid)

    def create_scientific_grid(self, parent_layout):
        grid = QGridLayout()
        layout = [
            ('DEG','RAD','INV','log','ln'),
            ('sin','cos','tan','(',')'),
            ('asin','acos','atan','^','|x|'),
            ('sinh','cosh','tanh','⌊x⌋','⌈x⌉'),
            ('nPr','nCr','x!','rand','EE'),
            ('7','8','9','÷','←'),
            ('4','5','6','×','C'),
            ('1','2','3','-','='),
            ('0','0','.','π','+')
        ]

        for r, row in enumerate(layout):
            for c, txt in enumerate(row):
                if txt == '0' and (r, c) != (8, 0):
                    continue
                if txt == '0':
                    btn = self.make_button('0')
                    grid.addWidget(btn, r, c, 1, 2)
                    continue
                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        parent_layout.addLayout(grid)

    def make_button(self, text):
        btn = QPushButton(text)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.clicked.connect(lambda checked, t=text: self.button_click(t))
        return btn

    # ---------- event handling ----------
    def button_click(self, value):
        try:
            # Numeric entry
            if value.isdigit():
                if self.should_reset:
                    self.current_number = value
                    self.should_reset = False
                else:
                    self.current_number = self.current_number if self.current_number != '0' else ''
                    self.current_number += value

            elif value == '.':
                if '.' not in self.current_number:
                    self.current_number += '.'

            elif value in ('π','e'):
                self.current_number = str(math.pi if value == 'π' else math.e)
                self.should_reset = True

            elif value == '←':
                self.current_number = self.current_number[:-1] if len(self.current_number) > 1 else '0'

            elif value in ('C',):
                self.clear()

            elif value == '±':
                if self.current_number and self.current_number != '0':
                    if self.current_number.startswith('-'):
                        self.current_number = self.current_number[1:]
                    else:
                        self.current_number = '-' + self.current_number

            elif value == '%':
                try:
                    self.current_number = str(float(self.current_number) / 100.0)
                except Exception:
                    self.current_number = 'Error'

            elif value in ('+', '-', '×', '÷', '^', 'nPr', 'nCr'):
                # store operator
                try:
                    self.last_number = float(self.current_number)
                except Exception:
                    self.last_number = 0.0
                self.operation = value
                self.should_reset = True

            elif value == '=':
                self.execute_operation()

            elif value == 'rand':
                self.current_number = str(np.random.random())

            elif value == 'x²':
                try:
                    v = float(self.current_number)
                    self.current_number = str(v * v)
                except Exception:
                    self.current_number = 'Error'

            elif value == '√':
                try:
                    v = float(self.current_number)
                    self.current_number = str(math.sqrt(v))
                except Exception:
                    self.current_number = 'Error'

            elif value == 'x!':
                try:
                    self.current_number = str(core.factorial(float(self.current_number)))
                except Exception:
                    self.current_number = 'Error'

            # update display for both tabs to be consistent (active tab shown)
            self.update_display()

        except Exception:
            self.current_number = 'Error'
            self.update_display()

    def execute_operation(self):
        try:
            if self.operation is None or self.last_number is None:
                return
            cur = float(self.current_number)
            if self.operation == '+':
                res = core.safe_add(self.last_number, cur)
            elif self.operation == '-':
                res = core.safe_sub(self.last_number, cur)
            elif self.operation == '×':
                res = core.safe_mul(self.last_number, cur)
            elif self.operation == '÷':
                res = core.safe_div(self.last_number, cur)
            elif self.operation == '^':
                res = core.power(self.last_number, cur)
            elif self.operation == 'nPr':
                res = core.nPr(self.last_number, cur)
            elif self.operation == 'nCr':
                res = core.nCr(self.last_number, cur)
            else:
                res = cur

            # Add operation to history
            result = core.format_result(res)
            if not result.startswith('Error'):
                self.history.insert(0, (f"{self.last_number} {self.operation} {cur}", result))
                if len(self.history) > 100:
                    self.history = self.history[:100]
                if hasattr(self, 'history_list'):
                    self.update_history_display()

            self.current_number = result
            self.operation = None
            self.last_number = None
            self.should_reset = True
        except Exception:
            self.current_number = 'Error'

    def clear(self):
        self.current_number = '0'
        self.operation = None
        self.last_number = None
        self.should_reset = False

    def update_display(self):
        # update both displays but active tab will be visible
        try:
            self.basic_display.setText(self.current_number)
            self.scientific_display.setText(self.current_number)
        except Exception:
            pass

    # ---------- Graphing ----------
    def setup_graphing_tab(self):
        """Create the graphing interface similar to TI-84"""
        controls = QHBoxLayout()

        # Function input
        func_group = QGroupBox("Y=")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Enter function (e.g., x^2)")
        plot_btn = QPushButton("Plot")
        plot_btn.clicked.connect(self.plot_function)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_plot)
        func_layout.addWidget(self.func_input)
        func_layout.addWidget(plot_btn)
        func_layout.addWidget(clear_btn)
        func_group.setLayout(func_layout)
        controls.addWidget(func_group)

        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        self.window_inputs = {}
        for name in ['xmin', 'xmax', 'ymin', 'ymax', 'xscl', 'yscl']:
            inp = QLineEdit()
            inp.setValidator(QDoubleValidator())
            self.window_inputs[name] = inp
            window_layout.addRow(name.capitalize(), inp)

        defaults = {'xmin': '-10', 'xmax': '10', 'ymin': '-10', 'ymax': '10', 'xscl': '1', 'yscl': '1'}
        for name, value in defaults.items():
            self.window_inputs[name].setText(value)

        update_btn = QPushButton("Update Window")
        update_btn.clicked.connect(self.update_window)
        window_layout.addWidget(update_btn)

        zoom_layout = QHBoxLayout()
        zoom_in = QPushButton("Zoom In (×2)")
        zoom_out = QPushButton("Zoom Out (÷2)")
        zoom_std = QPushButton("Standard")
        zoom_in.clicked.connect(lambda: self.zoom_graph(2))
        zoom_out.clicked.connect(lambda: self.zoom_graph(0.5))
        zoom_std.clicked.connect(self.reset_graph_view)
        zoom_layout.addWidget(zoom_in)
        zoom_layout.addWidget(zoom_out)
        zoom_layout.addWidget(zoom_std)
        window_layout.addRow(zoom_layout)

        window_group.setLayout(window_layout)
        controls.addWidget(window_group)

        # Analysis controls
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()

        trace_layout = QHBoxLayout()
        self.trace_x = QLineEdit()
        self.trace_x.setPlaceholderText("X value")
        self.trace_x.setValidator(QDoubleValidator())
        trace_btn = QPushButton("Trace")
        trace_btn.clicked.connect(self.trace_point)
        trace_layout.addWidget(self.trace_x)
        trace_layout.addWidget(trace_btn)
        analysis_layout.addLayout(trace_layout)

        btn_layout = QHBoxLayout()
        zeros_btn = QPushButton("Find Zeros")
        intersect_btn = QPushButton("Intersections")
        critical_btn = QPushButton("Critical Points")
        clear_pts_btn = QPushButton("Clear Points")

        zeros_btn.clicked.connect(self.find_zeros)
        intersect_btn.clicked.connect(self.find_intersections)
        critical_btn.clicked.connect(self.find_critical_points)
        clear_pts_btn.clicked.connect(lambda: self.graph_canvas.clear_points())

        btn_layout.addWidget(zeros_btn)
        btn_layout.addWidget(intersect_btn)
        btn_layout.addWidget(critical_btn)
        btn_layout.addWidget(clear_pts_btn)
        analysis_layout.addLayout(btn_layout)

        self.analysis_result = QLabel("")
        analysis_layout.addWidget(self.analysis_result)

        analysis_group.setLayout(analysis_layout)
        controls.addWidget(analysis_group)

        self.graphing_layout.addLayout(controls)

        # plotting canvas
        self.graph_canvas = graphing.GraphCanvas(self)
        self.graphing_layout.addWidget(self.graph_canvas)

    def plot_function(self):
        expr = self.func_input.text().strip()
        if expr:
            self.graph_calc.add_function(expr)
            self.graph_canvas.plot_function(expr)

    def clear_plot(self):
        self.graph_calc.clear_functions()
        self.func_input.clear()
        self.graph_canvas.setup_axes()
        self.graph_canvas.draw()

    def update_window(self):
        try:
            values = {name: float(inp.text()) for name, inp in self.window_inputs.items()}
            self.graph_canvas.set_window(**values)
            self.graph_canvas.setup_axes()
            for func in self.graph_calc.get_functions():
                self.graph_canvas.plot_function(func)
        except Exception:
            pass

    def zoom_graph(self, factor):
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            ymin = float(self.window_inputs['ymin'].text())
            ymax = float(self.window_inputs['ymax'].text())

            xcenter = (xmax + xmin) / 2
            ycenter = (ymax + ymin) / 2

            xrange = (xmax - xmin) / factor
            yrange = (ymax - ymin) / factor

            self.window_inputs['xmin'].setText(f"{xcenter - xrange/2:.2f}")
            self.window_inputs['xmax'].setText(f"{xcenter + xrange/2:.2f}")
            self.window_inputs['ymin'].setText(f"{ycenter - yrange/2:.2f}")
            self.window_inputs['ymax'].setText(f"{ycenter + yrange/2:.2f}")

            self.update_window()
        except Exception:
            pass

    def reset_graph_view(self):
        self.window_inputs['xmin'].setText("-10")
        self.window_inputs['xmax'].setText("10")
        self.window_inputs['ymin'].setText("-10")
        self.window_inputs['ymax'].setText("10")
        self.window_inputs['xscl'].setText("1")
        self.window_inputs['yscl'].setText("1")
        self.update_window()

    def trace_point(self):
        try:
            x = float(self.trace_x.text())
            expr = self.func_input.text().strip()
            if expr:
                y = self.graph_canvas.trace_function(expr, x)
                if y is not None:
                    self.graph_canvas.plot_point(x, y)
                    self.analysis_result.setText(f"Point: ({x:.3f}, {y:.3f})")
                else:
                    self.analysis_result.setText("Could not evaluate function at this point")
        except ValueError:
            self.analysis_result.setText("Invalid x value")

    def find_zeros(self):
        expr = self.func_input.text().strip()
        if not expr:
            return
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            zeros = self.graph_calc.find_zeros(expr, xmin, xmax)
            if zeros:
                for x in zeros:
                    self.graph_canvas.plot_point(x, 0, color='green')
                zeros_str = ", ".join(f"x = {x:.3f}" for x in zeros)
                self.analysis_result.setText(f"Zeros found: {zeros_str}")
            else:
                self.analysis_result.setText("No zeros found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding zeros: {str(e)}")

    def find_intersections(self):
        try:
            expr1 = self.func_input.text().strip()
            if not expr1:
                self.analysis_result.setText("Enter first function")
                return
            expr2, ok = QInputDialog.getText(self, "Find Intersections", "Enter second function:")
            if ok and expr2:
                xmin = float(self.window_inputs['xmin'].text())
                xmax = float(self.window_inputs['xmax'].text())
                points = self.graph_calc.find_intersections(expr1, expr2, xmin, xmax)
                if points:
                    for x, y in points:
                        self.graph_canvas.plot_point(x, y, color='blue')
                    points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                    self.analysis_result.setText(f"Intersections: {points_str}")
                else:
                    self.analysis_result.setText("No intersections found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding intersections: {str(e)}")

    def find_critical_points(self):
        expr = self.func_input.text().strip()
        if not expr:
            return
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            points = self.graph_calc.find_critical_points(expr, xmin, xmax)
            if points:
                for x, y in points:
                    self.graph_canvas.plot_point(x, y, color='purple')
                points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                self.analysis_result.setText(f"Critical points: {points_str}")
            else:
                self.analysis_result.setText("No critical points found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding critical points: {str(e)}")

    # ---------- History tab ----------
    def setup_history_tab(self):
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.history_list = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)

        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_content.setStyleSheet("background-color: rgba(0,0,0,0.03); border-radius: 5px; padding: 10px;")

        self.history_layout.addWidget(scroll)

        controls = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        controls.addWidget(clear_btn)
        controls.addStretch()
        self.history_layout.addLayout(controls)

        self.update_history_display()

    def clear_history(self):
        self.history = []
        self.update_history_display()

    def recall_history(self, value):
        self.current_number = value
        self.update_display()
        self.tabs.setCurrentIndex(0)

    def update_history_display(self):
        # Clear existing items
        while self.history_list.count():
            item = self.history_list.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for expr, result in self.history:
            row = QWidget()
            layout = QHBoxLayout(row)
            label = QLabel(f"{expr} = {result}")
            label.setWordWrap(True)
            recall = QPushButton("Recall")
            recall.setMaximumWidth(80)
            recall.clicked.connect(lambda _, v=result: self.recall_history(v))
            layout.addWidget(label)
            layout.addWidget(recall)
            self.history_list.addWidget(row)

        self.history_list.addStretch()

    # ---------- Theme / styles ----------
    def set_styles(self):
        self.current_theme = 'dark'
        self.apply_theme()

    def apply_theme(self):
        try:
            theme_file = Path(__file__).parent / 'styles' / 'themes' / f'{self.current_theme}.qss'
            if theme_file.exists():
                self.setStyleSheet(theme_file.read_text())
                if self.current_theme == 'dark':
                    self.theme_btn.setText("☀️ Light Mode")
                else:
                    self.theme_btn.setText("🌙 Dark Mode")
        except Exception:
            self.setStyleSheet('QWidget { background: #2b3136 }')

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()


def run_app():
    app = QApplication(sys.argv)
    w = CalculatorGUI()
    w.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(run_app())
"""
GUI for the calculator. Uses PyQt5. Keeps UI concerns separate from core logic.
"""
import sys
import math
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
    QHBoxLayout, QGroupBox, QFormLayout, QInputDialog, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator
from pathlib import Path
from . import core
from . import graphing


class CalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(800, 640)

        # State
        self.current_number = "0"
        self.operation = None
        self.last_number = None
        self.should_reset = False
        self.memory = 0.0
        self.angle_mode = "DEG"
        self.graph_calc = graphing.GraphingCalculator()

        # History tracking
        self.history = []  # List of (expression, result) tuples

        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        # Theme toggle
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setObjectName("theme-toggle")
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Basic tab
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        self.basic_display = QLabel("0")
        self.basic_display.setObjectName("display")
        self.basic_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.basic_display.setFont(QFont('Monospace', 24))
        self.basic_layout.addWidget(self.basic_display)
        self.create_basic_grid(self.basic_layout)
        self.tabs.addTab(self.basic_tab, "Basic")

        # Scientific tab
        self.scientific_tab = QWidget()
        self.scientific_layout = QVBoxLayout(self.scientific_tab)
        self.scientific_display = QLabel("0")
        self.scientific_display.setObjectName("display")
        self.scientific_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scientific_display.setFont(QFont('Monospace', 20))
        self.scientific_layout.addWidget(self.scientific_display)
        self.create_scientific_grid(self.scientific_layout)
        self.tabs.addTab(self.scientific_tab, "Scientific")

        # Graphing tab
        self.graphing_page = QWidget()
        self.graphing_layout = QVBoxLayout(self.graphing_page)
        self.setup_graphing_tab()
        self.tabs.addTab(self.graphing_page, "Graph")

        # History tab
        self.history_tab = QWidget()
        self.history_layout = QVBoxLayout(self.history_tab)
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, "History")

        self.set_styles()

    def create_basic_grid(self, parent_layout):
        grid = QGridLayout()
        labels = [
            ('MC','MR','M+','M-','C'),
            ('±','√','%','÷','←'),
            ('7','8','9','×','x²'),
            ('4','5','6','-','1/x'),
            ('1','2','3','+','='),
        ]

        for r, row in enumerate(labels):
            for c, txt in enumerate(row):
                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        # last row with 0 spanning
        zero = self.make_button('0')
        grid.addWidget(zero, 5, 0, 1, 2)
        grid.addWidget(self.make_button('.'), 5, 2)
        grid.addWidget(self.make_button('π'), 5, 3)
        grid.addWidget(self.make_button('e'), 5, 4)

        parent_layout.addLayout(grid)

    def create_scientific_grid(self, parent_layout):
        grid = QGridLayout()
        layout = [
            ('DEG','RAD','INV','log','ln'),
            ('sin','cos','tan','(',')'),
            ('asin','acos','atan','^','|x|'),
            ('sinh','cosh','tanh','⌊x⌋','⌈x⌉'),
            ('nPr','nCr','x!','rand','EE'),
            ('7','8','9','÷','←'),
            ('4','5','6','×','C'),
            ('1','2','3','-','='),
            ('0','0','.','π','+')
        ]

        for r, row in enumerate(layout):
            for c, txt in enumerate(row):
                if txt == '0' and (r, c) != (8, 0):
                    continue
                if txt == '0':
                    btn = self.make_button('0')
                    grid.addWidget(btn, r, c, 1, 2)
                    continue
                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        parent_layout.addLayout(grid)

    def make_button(self, text):
        btn = QPushButton(text)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.clicked.connect(lambda checked, t=text: self.button_click(t))
        return btn

    def button_click(self, value):
        try:
            if value.isdigit():
                if self.should_reset:
                    self.current_number = value
                    self.should_reset = False
                else:
                    self.current_number = self.current_number if self.current_number != '0' else ''
                    self.current_number += value
            elif value == '.':
                if '.' not in self.current_number:
                    self.current_number += '.'
            elif value in ('π','e'):
                self.current_number = str(math.pi if value == 'π' else math.e)
                self.should_reset = True
            elif value == '←':
                self.current_number = self.current_number[:-1] if len(self.current_number) > 1 else '0'
            elif value in ('C',):
                self.clear()
            elif value == '±':
                if self.current_number and self.current_number != '0':
                    if self.current_number.startswith('-'):
                        self.current_number = self.current_number[1:]
                    else:
                        self.current_number = '-' + self.current_number
            elif value == '%':
                try:
                    self.current_number = str(float(self.current_number) / 100.0)
                except Exception:
                    self.current_number = 'Error'
            elif value in ('+', '-', '×', '÷', '^', 'nPr', 'nCr'):
                try:
                    self.last_number = float(self.current_number)
                except Exception:
                    self.last_number = 0.0
                self.operation = value
                self.should_reset = True
            elif value == '=':
                self.execute_operation()
            elif value == 'rand':
                self.current_number = str(np.random.random())
            elif value == 'x²':
                try:
                    v = float(self.current_number)
                    self.current_number = str(v * v)
                except Exception:
                    self.current_number = 'Error'
            elif value == '√':
                try:
                    v = float(self.current_number)
                    self.current_number = str(math.sqrt(v))
                except Exception:
                    self.current_number = 'Error'
            elif value == 'x!':
                try:
                    self.current_number = str(core.factorial(float(self.current_number)))
                except Exception:
                    self.current_number = 'Error'
            self.update_display()
        except Exception:
            self.current_number = 'Error'
            self.update_display()

    def execute_operation(self):
        try:
            if self.operation is None or self.last_number is None:
                return
            cur = float(self.current_number)
            if self.operation == '+':
                res = core.safe_add(self.last_number, cur)
            elif self.operation == '-':
                res = core.safe_sub(self.last_number, cur)
            elif self.operation == '×':
                res = core.safe_mul(self.last_number, cur)
            elif self.operation == '÷':
                res = core.safe_div(self.last_number, cur)
            elif self.operation == '^':
                res = core.power(self.last_number, cur)
            elif self.operation == 'nPr':
                res = core.nPr(self.last_number, cur)
            elif self.operation == 'nCr':
                res = core.nCr(self.last_number, cur)
            else:
                res = cur
            result = core.format_result(res)
            if not result.startswith('Error'):
                self.history.insert(0, (f"{self.last_number} {self.operation} {cur}", result))
                if len(self.history) > 100:
                    self.history = self.history[:100]
                if hasattr(self, 'history_list'):
                    self.update_history_display()
            self.current_number = result
            self.operation = None
            self.last_number = None
            self.should_reset = True
        except Exception:
            self.current_number = 'Error'

    def clear(self):
        self.current_number = '0'
        self.operation = None
        self.last_number = None
        self.should_reset = False

    def update_display(self):
        # update both displays but active tab will be visible
        try:
            self.basic_display.setText(self.current_number)
            self.scientific_display.setText(self.current_number)
        except Exception:
            pass

    def setup_graphing_tab(self):
        controls = QHBoxLayout()
        func_group = QGroupBox("Y=")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Enter function (e.g., x^2)")
        plot_btn = QPushButton("Plot")
        plot_btn.clicked.connect(self.plot_function)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_plot)
        func_layout.addWidget(self.func_input)
        func_layout.addWidget(plot_btn)
        func_layout.addWidget(clear_btn)
        func_group.setLayout(func_layout)
        controls.addWidget(func_group)
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        self.window_inputs = {}
        for name in ['Xmin', 'Xmax', 'Ymin', 'Ymax', 'Xscl', 'Yscl']:
            inp = QLineEdit()
            inp.setValidator(QDoubleValidator())
            self.window_inputs[name.lower()] = inp
            window_layout.addRow(name, inp)
        defaults = {'xmin': '-10', 'xmax': '10', 'ymin': '-10', 'ymax': '10', 'xscl': '1', 'yscl': '1'}
        for name, value in defaults.items():
            self.window_inputs[name].setText(value)
        update_btn = QPushButton("Update Window")
        update_btn.clicked.connect(self.update_window)
        window_layout.addWidget(update_btn)
        zoom_layout = QHBoxLayout()
        zoom_in = QPushButton("Zoom In (×2)")
        zoom_out = QPushButton("Zoom Out (÷2)")
        zoom_std = QPushButton("Standard")
        zoom_in.clicked.connect(lambda: self.zoom_graph(2))
        zoom_out.clicked.connect(lambda: self.zoom_graph(0.5))
        zoom_std.clicked.connect(self.reset_graph_view)
        zoom_layout.addWidget(zoom_in)
        zoom_layout.addWidget(zoom_out)
        zoom_layout.addWidget(zoom_std)
        window_layout.addLayout(zoom_layout)
        window_group.setLayout(window_layout)
        controls.addWidget(window_group)
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()
        trace_layout = QHBoxLayout()
        self.trace_x = QLineEdit()
        self.trace_x.setPlaceholderText("X value")
        self.trace_x.setValidator(QDoubleValidator())
        trace_btn = QPushButton("Trace")
        trace_btn.clicked.connect(self.trace_point)
        trace_layout.addWidget(self.trace_x)
        trace_layout.addWidget(trace_btn)
        analysis_layout.addLayout(trace_layout)
        btn_layout = QHBoxLayout()
        zeros_btn = QPushButton("Find Zeros")
        intersect_btn = QPushButton("Intersections")
        critical_btn = QPushButton("Critical Points")
        clear_btn = QPushButton("Clear Points")
        zeros_btn.clicked.connect(self.find_zeros)
        intersect_btn.clicked.connect(self.find_intersections)
        critical_btn.clicked.connect(self.find_critical_points)
        clear_btn.clicked.connect(lambda: self.graph_canvas.clear_points())
        btn_layout.addWidget(zeros_btn)
        btn_layout.addWidget(intersect_btn)
        btn_layout.addWidget(critical_btn)
        btn_layout.addWidget(clear_btn)
        analysis_layout.addLayout(btn_layout)
        self.analysis_result = QLabel("")
        analysis_layout.addWidget(self.analysis_result)
        analysis_group.setLayout(analysis_layout)
        controls.addWidget(analysis_group)
        self.graphing_layout.addLayout(controls)
        self.graph_canvas = graphing.GraphCanvas(self)
        self.graphing_layout.addWidget(self.graph_canvas)
    def plot_function(self):
        expr = self.func_input.text().strip()
        if expr:
            self.graph_calc.add_function(expr)
            self.graph_canvas.plot_function(expr)
    def clear_plot(self):
        self.graph_calc.clear_functions()
        self.func_input.clear()
        self.graph_canvas.setup_axes()
        self.graph_canvas.draw()
    def update_window(self):
        try:
            values = {name: float(inp.text()) for name, inp in self.window_inputs.items()}
            self.graph_canvas.set_window(**values)
            self.graph_canvas.setup_axes()
            for func in self.graph_calc.get_functions():
                self.graph_canvas.plot_function(func)
        except ValueError:
            pass
    def zoom_graph(self, factor):
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            ymin = float(self.window_inputs['ymin'].text())
            ymax = float(self.window_inputs['ymax'].text())
            xcenter = (xmax + xmin) / 2
            ycenter = (ymax + ymin) / 2
            xrange = (xmax - xmin) / factor
            yrange = (ymax - ymin) / factor
            self.window_inputs['xmin'].setText(f"{xcenter - xrange/2:.2f}")
            self.window_inputs['xmax'].setText(f"{xcenter + xrange/2:.2f}")
            self.window_inputs['ymin'].setText(f"{ycenter - yrange/2:.2f}")
            self.window_inputs['ymax'].setText(f"{ycenter + yrange/2:.2f}")
            self.update_window()
        except ValueError:
            pass
    def reset_graph_view(self):
        self.window_inputs['xmin'].setText("-10")
        self.window_inputs['xmax'].setText("10")
        self.window_inputs['ymin'].setText("-10")
        self.window_inputs['ymax'].setText("10")
        self.window_inputs['xscl'].setText("1")
        self.window_inputs['yscl'].setText("1")
        self.update_window()
    def trace_point(self):
        try:
            x = float(self.trace_x.text())
            expr = self.func_input.text().strip()
            if expr:
                y = self.graph_canvas.trace_function(expr, x)
                if y is not None:
                    self.graph_canvas.plot_point(x, y)
                    self.analysis_result.setText(f"Point: ({x:.3f}, {y:.3f})")
                else:
                    self.analysis_result.setText("Could not evaluate function at this point")
        except ValueError:
            self.analysis_result.setText("Invalid x value")
    def find_zeros(self):
        expr = self.func_input.text().strip()
        if not expr:
            return
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            zeros = self.graph_calc.find_zeros(expr, xmin, xmax)
            if zeros:
                for x in zeros:
                    self.graph_canvas.plot_point(x, 0, color='green')
                zeros_str = ", ".join(f"x = {x:.3f}" for x in zeros)
                self.analysis_result.setText(f"Zeros found: {zeros_str}")
            else:
                self.analysis_result.setText("No zeros found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding zeros: {str(e)}")
    def find_intersections(self):
        try:
            expr1 = self.func_input.text().strip()
            if not expr1:
                self.analysis_result.setText("Enter first function")
                return
            expr2, ok = QInputDialog.getText(self, "Find Intersections", "Enter second function:")
            if ok and expr2:
                xmin = float(self.window_inputs['xmin'].text())
                xmax = float(self.window_inputs['xmax'].text())
                points = self.graph_calc.find_intersections(expr1, expr2, xmin, xmax)
                if points:
                    for x, y in points:
                        self.graph_canvas.plot_point(x, y, color='blue')
                    points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                    self.analysis_result.setText(f"Intersections: {points_str}")
                else:
                    self.analysis_result.setText("No intersections found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding intersections: {str(e)}")
    def find_critical_points(self):
        expr = self.func_input.text().strip()
        if not expr:
            return
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            points = self.graph_calc.find_critical_points(expr, xmin, xmax)
            if points:
                for x, y in points:
                    self.graph_canvas.plot_point(x, y, color='purple')
                points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                self.analysis_result.setText(f"Critical points: {points_str}")
            else:
                self.analysis_result.setText("No critical points found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding critical points: {str(e)}")
    def setup_history_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.history_list = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_content.setStyleSheet("background-color: rgba(0,0,0,0.05); border-radius: 5px; padding: 10px;")
        self.history_layout.addWidget(scroll)
        controls = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        controls.addWidget(clear_btn)
        controls.addStretch()
        self.history_layout.addLayout(controls)
        self.update_history_display()
    def clear_history(self):
        self.history = []
        self.update_history_display()
    def recall_history(self, value):
        self.current_number = value
        self.update_display()
        self.tabs.setCurrentIndex(0)
    def update_history_display(self):
        while self.history_list.count():
            item = self.history_list.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for expr, result in self.history:
            row = QWidget()
            layout = QHBoxLayout(row)
            label = QLabel(f"{expr} = {result}")
            label.setWordWrap(True)
            recall = QPushButton("Recall")
            recall.setMaximumWidth(80)
            recall.clicked.connect(lambda _, v=result: self.recall_history(v))
            layout.addWidget(label)
            layout.addWidget(recall)
            self.history_list.addWidget(row)
        self.history_list.addStretch()
    def set_styles(self):
        self.current_theme = 'dark'
        self.apply_theme()
    def apply_theme(self):
        try:
            theme_file = Path(__file__).parent / 'styles' / 'themes' / f'{self.current_theme}.qss'
            if theme_file.exists():
                self.setStyleSheet(theme_file.read_text())
                if self.current_theme == 'dark':
                    self.theme_btn.setText("☀️ Light Mode")
                else:
                    self.theme_btn.setText("🌙 Dark Mode")
        except Exception:
            self.setStyleSheet('QWidget { background: #2b3136 }')
    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()
def run_app():
    app = QApplication(sys.argv)
    w = CalculatorGUI()
    w.show()
    return app.exec_()
if __name__ == '__main__':
    sys.exit(run_app())"""
GUI for the calculator. Uses PyQt5. Keeps UI concerns separate from core logic.
"""
import sys
import math
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
    QHBoxLayout, QGroupBox, QFormLayout, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator
from pathlib import Path
from . import core
from . import graphing


class CalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(800, 640)

        # State
        self.current_number = "0"
        self.operation = None
        self.last_number = None
        self.should_reset = False
        self.memory = 0.0
        self.angle_mode = "DEG"
        self.graph_calc = graphing.GraphingCalculator()
        
        # History tracking
        self.history = []  # List of (expression, result) tuples
        self.history_selected = None

        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        # Theme toggle
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setObjectName("theme-toggle")
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Basic tab
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        self.basic_display = QLabel("0")
        self.basic_display.setObjectName("display")
        self.basic_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.basic_display.setFont(QFont('Monospace', 24))
        self.basic_layout.addWidget(self.basic_display)
        self.create_basic_grid(self.basic_layout)
        self.tabs.addTab(self.basic_tab, "Basic")

        # Scientific tab
        self.scientific_tab = QWidget()
        self.scientific_layout = QVBoxLayout(self.scientific_tab)
        self.scientific_display = QLabel("0")
        self.scientific_display.setObjectName("display")
        self.scientific_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scientific_display.setFont(QFont('Monospace', 20))
        self.scientific_layout.addWidget(self.scientific_display)
        self.create_scientific_grid(self.scientific_layout)
        self.tabs.addTab(self.scientific_tab, "Scientific")

        # Create graphing tab
        self.graphing_page = QWidget()
        self.graphing_layout = QVBoxLayout(self.graphing_page)
        self.setup_graphing_tab()
        self.tabs.addTab(self.graphing_page, "Graph")

        # Add history tab
        self.history_tab = QWidget()
        self.history_layout = QVBoxLayout(self.history_tab)
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, "History")

        self.set_styles()

    # ---------- UI builders ----------
    def create_basic_grid(self, parent_layout):
        grid = QGridLayout()
        # Define a fixed 6x5 grid for basic page
        labels = [
            ('MC','MR','M+','M-','C'),
            ('±','√','%','÷','←'),
            ('7','8','9','×','x²'),
            ('4','5','6','-','1/x'),
            ('1','2','3','+','=')
        ]

        # last row handled separately to allow 0 spanning two columns
        last_row = ('0','0','.','π','e')
        for r, row in enumerate(labels):
            for c, txt in enumerate(row):
                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        # add last row
        for c, txt in enumerate(last_row):
            if txt == '0' and c == 0:
                btn = self.make_button('0')
                grid.addWidget(btn, len(labels), 0, 1, 2)
            elif txt == '0':
                continue
            else:
                btn = self.make_button(txt)
                col = c if c < 2 else c+0
                grid.addWidget(btn, len(labels), col if c>1 else c+2)

        parent_layout.addLayout(grid)

    def create_scientific_grid(self, parent_layout):
        grid = QGridLayout()
        layout = [
            ('DEG','RAD','INV','log','ln'),
            ('sin','cos','tan','(',')'),
            ('asin','acos','atan','^','|x|'),
            ('sinh','cosh','tanh','⌊x⌋','⌈x⌉'),
            ('nPr','nCr','x!','rand','EE'),
            ('7','8','9','÷','←'),
            ('4','5','6','×','C'),
            ('1','2','3','-','='),
            ('0','0','.','π','+')
        ]

        for r, row in enumerate(layout):
            for c, txt in enumerate(row):
                if txt == '0' and (r, c) != (8, 0):
                    continue
                if txt == '0':
                    btn = self.make_button('0')
                    grid.addWidget(btn, r, c, 1, 2)
                    continue
                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        parent_layout.addLayout(grid)

    def make_button(self, text):
        btn = QPushButton(text)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.clicked.connect(lambda checked, t=text: self.button_click(t))
        return btn

    # ---------- event handling ----------
    def button_click(self, value):
        # Use the common handler but update the display of the active tab
        try:
            # Numeric entry
            if value.isdigit():
                if self.should_reset:
                    self.current_number = value
                    self.should_reset = False
                else:
                    self.current_number = self.current_number if self.current_number != '0' else ''
                    self.current_number += value

            elif value == '.':
                if '.' not in self.current_number:
                    self.current_number += '.'

            elif value in ('π','e'):
                self.current_number = str(math.pi if value == 'π' else math.e)
                self.should_reset = True

            elif value == '←':
                self.current_number = self.current_number[:-1] if len(self.current_number) > 1 else '0'

            elif value in ('C',):
                self.clear()

            elif value == '±':
                if self.current_number and self.current_number != '0':
                    if self.current_number.startswith('-'):
                        self.current_number = self.current_number[1:]
                    else:
                        self.current_number = '-' + self.current_number

            elif value == '%':
                try:
                    self.current_number = str(float(self.current_number) / 100.0)
                except Exception:
                    self.current_number = 'Error'

            elif value in ('+', '-', '×', '÷', '^', 'nPr', 'nCr'):
                # store operator
                try:
                    self.last_number = float(self.current_number)
                except Exception:
                    self.last_number = 0.0
                self.operation = value
                self.should_reset = True

            elif value == '=':
                self.execute_operation()

            elif value == 'rand':
                self.current_number = str(np.random.random())

            elif value == 'x²':
                try:
                    v = float(self.current_number)
                    self.current_number = str(v * v)
                except Exception:
                    self.current_number = 'Error'

            elif value == '√':
                try:
                    v = float(self.current_number)
                    self.current_number = str(math.sqrt(v))
                except Exception:
                    self.current_number = 'Error'

            elif value == 'x!':
                try:
                    self.current_number = str(core.factorial(float(self.current_number)))
                except Exception:
                    self.current_number = 'Error'

            # update display for both tabs to be consistent (active tab shown)
            self.update_display()

        except Exception:
            self.current_number = 'Error'
            self.update_display()

    def execute_operation(self):
        try:
            if self.operation is None or self.last_number is None:
                return
            cur = float(self.current_number)
            if self.operation == '+':
                res = core.safe_add(self.last_number, cur)
            elif self.operation == '-':
                res = core.safe_sub(self.last_number, cur)
            elif self.operation == '×':
                res = core.safe_mul(self.last_number, cur)
            elif self.operation == '÷':
                res = core.safe_div(self.last_number, cur)
            elif self.operation == '^':
                res = core.power(self.last_number, cur)
            elif self.operation == 'nPr':
                res = core.nPr(self.last_number, cur)
            elif self.operation == 'nCr':
                res = core.nCr(self.last_number, cur)
            else:
                res = cur

            # Add operation to history
            result = core.format_result(res)
            if not result.startswith('Error'):
                self.history.insert(0, (f"{self.last_number} {self.operation} {cur}", result))
                if len(self.history) > 100:
                    self.history = self.history[:100]
                if hasattr(self, 'history_list'):
                    self.update_history_display()

            self.current_number = result
            self.operation = None
            self.last_number = None
            self.should_reset = True
        except Exception:
            self.current_number = 'Error'

    def clear(self):
        self.current_number = '0'
        self.operation = None
        self.last_number = None
        self.should_reset = False

    def update_display(self):
        # update both displays but active tab will be visible
        self.basic_display.setText(self.current_number)
        self.scientific_display.setText(self.current_number)

    def setup_graphing_tab(self):
        """Create the graphing interface similar to TI-84"""
        # Top controls
        controls = QHBoxLayout()
        
        # Function input
        func_group = QGroupBox("Y=")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Enter function (e.g., x^2)")
        plot_btn = QPushButton("Plot")
        plot_btn.clicked.connect(self.plot_function)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_plot)
        func_layout.addWidget(self.func_input)
        func_layout.addWidget(plot_btn)
        func_layout.addWidget(clear_btn)
        func_group.setLayout(func_layout)
        controls.addWidget(func_group)
        
        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        self.window_inputs = {}
        for name in ['Xmin', 'Xmax', 'Ymin', 'Ymax', 'Xscl', 'Yscl']:
            inp = QLineEdit()
            inp.setValidator(QDoubleValidator())
            self.window_inputs[name.lower()] = inp
            window_layout.addRow(name, inp)
        
        # Set default window values
        defaults = {'xmin': '-10', 'xmax': '10', 'ymin': '-10', 
                   'ymax': '10', 'xscl': '1', 'yscl': '1'}
        for name, value in defaults.items():
            self.window_inputs[name].setText(value)
        
        update_btn = QPushButton("Update Window")
        update_btn.clicked.connect(self.update_window)
        window_layout.addWidget(update_btn)
        
        # Add zoom controls
        zoom_layout = QHBoxLayout()
        zoom_in = QPushButton("Zoom In (×2)")
        zoom_out = QPushButton("Zoom Out (÷2)")
        zoom_std = QPushButton("Standard")
        zoom_in.clicked.connect(lambda: self.zoom_graph(2))
        zoom_out.clicked.connect(lambda: self.zoom_graph(0.5))
        zoom_std.clicked.connect(self.reset_graph_view)
        zoom_layout.addWidget(zoom_in)
        zoom_layout.addWidget(zoom_out)
        zoom_layout.addWidget(zoom_std)
        window_layout.addLayout(zoom_layout)
        
        window_group.setLayout(window_layout)
        controls.addWidget(window_group)
        
        # Analysis controls
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()
        
        # Trace controls
        trace_layout = QHBoxLayout()
        self.trace_x = QLineEdit()
        self.trace_x.setPlaceholderText("X value")
        self.trace_x.setValidator(QDoubleValidator())
        trace_btn = QPushButton("Trace")
        trace_btn.clicked.connect(self.trace_point)
        trace_layout.addWidget(self.trace_x)
        trace_layout.addWidget(trace_btn)
        analysis_layout.addLayout(trace_layout)
        
        # Analysis buttons
        btn_layout = QHBoxLayout()
        zeros_btn = QPushButton("Find Zeros")
        intersect_btn = QPushButton("Intersections")
        critical_btn = QPushButton("Critical Points")
        clear_btn = QPushButton("Clear Points")
        
        zeros_btn.clicked.connect(self.find_zeros)
        intersect_btn.clicked.connect(self.find_intersections)
        critical_btn.clicked.connect(self.find_critical_points)
        clear_btn.clicked.connect(lambda: self.graph_canvas.clear_points())
        
        btn_layout.addWidget(zeros_btn)
        btn_layout.addWidget(intersect_btn)
        btn_layout.addWidget(critical_btn)
        btn_layout.addWidget(clear_btn)
        analysis_layout.addLayout(btn_layout)
        
        # Results display
        self.analysis_result = QLabel("")
        analysis_layout.addWidget(self.analysis_result)
        
        analysis_group.setLayout(analysis_layout)
        controls.addWidget(analysis_group)
        
        self.graphing_layout.addLayout(controls)
        
        # Add the plotting canvas
        self.graph_canvas = graphing.GraphCanvas(self)
        self.graphing_layout.addWidget(self.graph_canvas)

    def plot_function(self):
        """Plot the current function"""
        expr = self.func_input.text().strip()
        if expr:
            self.graph_calc.add_function(expr)
            self.graph_canvas.plot_function(expr)
    
    def clear_plot(self):
        """Clear all plotted functions"""
        self.graph_calc.clear_functions()
        self.func_input.clear()
        self.graph_canvas.setup_axes()
        self.graph_canvas.draw()
    
    def update_window(self):
        """Update the plotting window ranges"""
        try:
            values = {name: float(inp.text())
                     for name, inp in self.window_inputs.items()}
            self.graph_canvas.set_window(**values)
            
            # Replot all active functions
            self.graph_canvas.setup_axes()
            for func in self.graph_calc.get_functions():
                self.graph_canvas.plot_function(func)
        except ValueError:
            pass  # Invalid number format - ignore
            
    def zoom_graph(self, factor):
        """Zoom in or out by the given factor"""
        try:
            # Get current window values
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            ymin = float(self.window_inputs['ymin'].text())
            ymax = float(self.window_inputs['ymax'].text())
            
            # Calculate center points
            xcenter = (xmax + xmin) / 2
            ycenter = (ymax + ymin) / 2
            
            # Calculator GUI - clean implementation
            # Provides a CalculatorGUI with Basic, Scientific, Graph and History tabs.

            import sys
            import math
            import numpy as np
            from pathlib import Path

            from PyQt5.QtWidgets import (
                QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
                QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
                QHBoxLayout, QFormLayout, QInputDialog, QScrollArea
            )
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont, QDoubleValidator

            from . import core
            from . import graphing


            class CalculatorGUI(QMainWindow):
                """Minimal, single-definition GUI implementation."""

                def __init__(self):
                    super().__init__()
                    self.setWindowTitle("Calculator")
                    self.setFixedSize(900, 650)

                    self.current_number = "0"
                    self.operation = None
                    self.last_number = None
                    self.should_reset = False
                    self.history = []

                    # graphing helper
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

                    # Calculator tab
                    calc = QWidget()
                    v = QVBoxLayout(calc)
                    self.display = QLabel(self.current_number)
                    self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.display.setFont(QFont('Monospace', 28))
                    v.addWidget(self.display)

                    grid = QGridLayout()
                    buttons = [
                        '7','8','9','÷',
                        '4','5','6','×',
                        '1','2','3','-',
                        '0','.','=','+'
                    ]
                    positions = [(r, c) for r in range(4) for c in range(4)]
                    for pos, txt in zip(positions, buttons):
                        btn = QPushButton(txt)
                        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        btn.clicked.connect(lambda _, t=txt: self.on_button(t))
                        grid.addWidget(btn, *pos)
                    v.addLayout(grid)

                    self.tabs.addTab(calc, "Calc")

                    # Graph tab (basic wiring)
                    graph = QWidget()
                    gv = QVBoxLayout(graph)
                    fh = QHBoxLayout()
                    self.func_input = QLineEdit()
                    self.func_input.setPlaceholderText("Enter function, e.g. x**2")
                    plot_btn = QPushButton("Plot")
                    plot_btn.clicked.connect(self.on_plot)
                    fh.addWidget(self.func_input)
                    fh.addWidget(plot_btn)
                    gv.addLayout(fh)

                    try:
                        self.canvas = graphing.GraphCanvas(self)
                        gv.addWidget(self.canvas)
                    except Exception:
                        self.canvas = None
                        gv.addWidget(QLabel("Graphing unavailable"))

                    self.tabs.addTab(graph, "Graph")

                    # History tab
                    hist = QWidget()
                    hv = QVBoxLayout(hist)
                    self.history_area = QScrollArea()
                    self.history_area.setWidgetResizable(True)
                    content = QWidget()
                    self.history_list = QVBoxLayout(content)
                    self.history_area.setWidget(content)
                    hv.addWidget(self.history_area)
                    clear_btn = QPushButton("Clear History")
                    clear_btn.clicked.connect(self.clear_history)
                    hv.addWidget(clear_btn)
                    self.tabs.addTab(hist, "History")

                # ---------- calculator ----------
                def on_button(self, text):
                    if text.isdigit():
                        if self.should_reset:
                            self.current_number = text
                            self.should_reset = False
                        else:
                            self.current_number = ('' if self.current_number == '0' else self.current_number) + text
                    elif text == '.':
                        if '.' not in self.current_number:
                            self.current_number += '.'
                    elif text in ('+', '-', '×', '÷'):
                        try:
                            self.last_number = float(self.current_number)
                        except Exception:
                            self.last_number = 0.0
                        self.operation = text
                        self.should_reset = True
                    elif text == '=':
                        self._compute()
                    self._refresh_display()

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

                def _refresh_display(self):
                    self.display.setText(str(self.current_number))

                # ---------- history ----------
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
                        btn = QPushButton("Recall")
                        btn.clicked.connect(lambda _, v=res: self.recall(v))
                        h.addWidget(lbl)
                        h.addWidget(btn)
                        self.history_list.addWidget(row)
                    self.history_list.addStretch()

                def recall(self, value):
                    self.current_number = value
                    self.tabs.setCurrentIndex(0)
                    self._refresh_display()

                def clear_history(self):
                    self.history = []
                    self.update_history_display()

                # ---------- graphing ----------
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
    QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
    QHBoxLayout, QGroupBox, QFormLayout, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator
from pathlib import Path
from . import core
from . import graphing


class CalculatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setFixedSize(800, 640)

        # State
        self.current_number = "0"
        self.operation = None
        self.last_number = None
        self.should_reset = False
        self.memory = 0.0
        self.angle_mode = "DEG"
        self.graph_calc = graphing.GraphingCalculator()
        
        # History tracking
        self.add_to_history('Memory Clear', '0')
        self.history = []  # List of (expression, result) tuples
        self.history_selected = None

        # Main widget
        self.main_widget = QWidget()
        self.add_to_history('Memory Add', str(self.memory))
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)
        self.add_to_history('Memory Subtract', str(self.memory))

        # Theme toggle
        theme_layout = QHBoxLayout()
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setObjectName("theme-toggle")
        self.theme_btn.clicked.connect(self.toggle_theme)
        input_val = str(x)  # Store input for history
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Basic tab
        self.add_to_history(f'arc{func}({input_val}°)', str(result))
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        self.add_to_history(f'{func}({input_val}°)', str(result))
        self.basic_display = QLabel("0")
        self.basic_display.setObjectName("display")
        self.add_to_history(f'{func}({input_val})', str(result))
        self.basic_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.basic_display.setFont(QFont('Monospace', 24))
        self.basic_layout.addWidget(self.basic_display)
        self.create_basic_grid(self.basic_layout)
        self.tabs.addTab(self.basic_tab, "Basic")

            def add_to_history(self, expr, result):
                """Add an operation to the history"""
                if not result.startswith('Error'):
                    self.history.insert(0, (expr, result))
                    # Keep history to reasonable size
                    if len(self.history) > 100:
                        self.history = self.history[:100]
                    # Update history display if tab exists
                    if hasattr(self, 'history_list'):
                        self.update_history_display()
        # Scientific tab
        self.scientific_tab = QWidget()
        self.scientific_layout = QVBoxLayout(self.scientific_tab)
        self.scientific_display = QLabel("0")
        self.scientific_display.setObjectName("display")
        self.scientific_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scientific_display.setFont(QFont('Monospace', 20))
        self.scientific_layout.addWidget(self.scientific_display)
        self.create_scientific_grid(self.scientific_layout)
        self.tabs.addTab(self.scientific_tab, "Scientific")

        # Create graphing tab
        self.graphing_page = QWidget()
        self.graphing_layout = QVBoxLayout(self.graphing_page)
        self.setup_graphing_tab()
        self.tabs.addTab(self.graphing_page, "Graph")

        self.set_styles()

    # ---------- UI builders ----------
    def create_basic_grid(self, parent_layout):
        grid = QGridLayout()
        # Define a fixed 6x5 grid for basic page
        labels = [
                    self.add_to_history(
                        f"{self.last_number} {self.operation} {cur}",
                        core.format_result(res)
                    )
            for c, txt in enumerate(row):
                # special case: when '0' appears twice we only create one button that spans two columns
                if txt == '0' and (r, c) != (5, 0):
                    # skip the duplicate placeholder
                    continue
                if txt == '0':
                    btn = self.make_button('0')
                    grid.addWidget(btn, r, c, 1, 2)
                    continue

                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        parent_layout.addLayout(grid)

    def create_scientific_grid(self, parent_layout):
        grid = QGridLayout()
        layout = [
            ('DEG','RAD','INV','log','ln'),
            ('sin','cos','tan','(',')'),
            ('asin','acos','atan','^','|x|'),
            ('sinh','cosh','tanh','⌊x⌋','⌈x⌉'),
            ('nPr','nCr','x!','rand','EE'),
            ('7','8','9','÷','←'),
            ('4','5','6','×','C'),
            ('1','2','3','-','='),
            ('0','0','.','π','+')
        ]

        for r, row in enumerate(layout):
            for c, txt in enumerate(row):
                if txt == '0' and (r, c) != (8, 0):
                    continue
                if txt == '0':
                    btn = self.make_button('0')
                    grid.addWidget(btn, r, c, 1, 2)
                    continue
                btn = self.make_button(txt)
                grid.addWidget(btn, r, c)

        parent_layout.addLayout(grid)

    def make_button(self, text):
        btn = QPushButton(text)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.clicked.connect(lambda checked, t=text: self.button_click(t))
        return btn

    # ---------- event handling ----------
    def button_click(self, value):
        # Use the common handler but update the display of the active tab
        try:
            # Numeric entry
            if value.isdigit():
                if self.should_reset:
                    self.current_number = value
                    self.should_reset = False
                else:
                    self.current_number = self.current_number if self.current_number != '0' else ''
                    self.current_number += value

            elif value == '.':
                if '.' not in self.current_number:
                    self.current_number += '.'

            elif value in ('π','e'):
                self.current_number = str(math.pi if value == 'π' else math.e)
                self.should_reset = True

            elif value == '←':
                self.current_number = self.current_number[:-1] if len(self.current_number) > 1 else '0'

            elif value in ('C',):
                self.clear()

            elif value == '±':
                if self.current_number and self.current_number != '0':
                    if self.current_number.startswith('-'):
                        self.current_number = self.current_number[1:]
                    else:
                        self.current_number = '-' + self.current_number

            elif value == '%':
                try:
                    self.current_number = str(float(self.current_number) / 100.0)
                except Exception:
                    self.current_number = 'Error'

            elif value in ('+', '-', '×', '÷', '^', 'nPr', 'nCr'):
                # store operator
                try:
                    self.last_number = float(self.current_number)
                except Exception:
                    self.last_number = 0.0
                self.operation = value
                self.should_reset = True

            elif value == '=':
                self.execute_operation()

            elif value == 'rand':
                self.current_number = str(np.random.random())

            elif value == 'x²':
                try:
                    v = float(self.current_number)
                    self.current_number = str(v * v)
                except Exception:
                    self.current_number = 'Error'

            elif value == '√':
                try:
                    v = float(self.current_number)
                    self.current_number = str(math.sqrt(v))
                except Exception:
                    self.current_number = 'Error'

            elif value == 'x!':
                try:
                    self.current_number = str(core.factorial(float(self.current_number)))
                except Exception:
                    self.current_number = 'Error'

            # update display for both tabs to be consistent (active tab shown)
            self.update_display()

        except Exception:
            self.current_number = 'Error'
            self.update_display()

    def execute_operation(self):
        try:
            if self.operation is None or self.last_number is None:
                return
            cur = float(self.current_number)
            if self.operation == '+':
                res = core.safe_add(self.last_number, cur)
            elif self.operation == '-':
                res = core.safe_sub(self.last_number, cur)
            elif self.operation == '×':
                res = core.safe_mul(self.last_number, cur)
            elif self.operation == '÷':
                res = core.safe_div(self.last_number, cur)
            elif self.operation == '^':
                res = core.power(self.last_number, cur)
            elif self.operation == 'nPr':
                res = core.nPr(self.last_number, cur)
            elif self.operation == 'nCr':
                res = core.nCr(self.last_number, cur)
            else:
                res = cur

            self.current_number = core.format_result(res)
            self.operation = None
            self.last_number = None
            self.should_reset = True
        except Exception:
            self.current_number = 'Error'

    def clear(self):
        self.current_number = '0'
        self.operation = None
        self.last_number = None
        self.should_reset = False

    def update_display(self):
        # update both displays but active tab will be visible
        self.basic_display.setText(self.current_number)
        self.scientific_display.setText(self.current_number)

    def setup_graphing_tab(self):
        """Create the graphing interface similar to TI-84"""
        # Top controls
        controls = QHBoxLayout()
        
        # Function input
        func_group = QGroupBox("Y=")
        func_layout = QVBoxLayout()
        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Enter function (e.g., x^2)")
        plot_btn = QPushButton("Plot")
        plot_btn.clicked.connect(self.plot_function)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_plot)
        func_layout.addWidget(self.func_input)
        func_layout.addWidget(plot_btn)
        func_layout.addWidget(clear_btn)
        func_group.setLayout(func_layout)
        controls.addWidget(func_group)
        
        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        self.window_inputs = {}
        for name in ['Xmin', 'Xmax', 'Ymin', 'Ymax', 'Xscl', 'Yscl']:
            inp = QLineEdit()
            inp.setValidator(QDoubleValidator())
            self.window_inputs[name.lower()] = inp
            window_layout.addRow(name, inp)
        
        # Set default window values
        defaults = {'xmin': '-10', 'xmax': '10', 'ymin': '-10', 
                   'ymax': '10', 'xscl': '1', 'yscl': '1'}
        for name, value in defaults.items():
            self.window_inputs[name].setText(value)
        
        update_btn = QPushButton("Update Window")
        update_btn.clicked.connect(self.update_window)
        window_layout.addWidget(update_btn)
        
        # Add zoom controls
        zoom_layout = QHBoxLayout()
        zoom_in = QPushButton("Zoom In (×2)")
        zoom_out = QPushButton("Zoom Out (÷2)")
        zoom_std = QPushButton("Standard")
        zoom_in.clicked.connect(lambda: self.zoom_graph(2))
        zoom_out.clicked.connect(lambda: self.zoom_graph(0.5))
        zoom_std.clicked.connect(self.reset_graph_view)
        zoom_layout.addWidget(zoom_in)
        zoom_layout.addWidget(zoom_out)
        zoom_layout.addWidget(zoom_std)
        window_layout.addLayout(zoom_layout)
        
        window_group.setLayout(window_layout)
        controls.addWidget(window_group)
        
        # Analysis controls
        analysis_group = QGroupBox("Analysis")
        analysis_layout = QVBoxLayout()
        
        # Trace controls
        trace_layout = QHBoxLayout()
        self.trace_x = QLineEdit()
        self.trace_x.setPlaceholderText("X value")
        self.trace_x.setValidator(QDoubleValidator())
        trace_btn = QPushButton("Trace")
        trace_btn.clicked.connect(self.trace_point)
        trace_layout.addWidget(self.trace_x)
        trace_layout.addWidget(trace_btn)
        analysis_layout.addLayout(trace_layout)
        
        # Analysis buttons
        btn_layout = QHBoxLayout()
        zeros_btn = QPushButton("Find Zeros")
        intersect_btn = QPushButton("Intersections")
        critical_btn = QPushButton("Critical Points")
        clear_btn = QPushButton("Clear Points")
        
        zeros_btn.clicked.connect(self.find_zeros)
        intersect_btn.clicked.connect(self.find_intersections)
        critical_btn.clicked.connect(self.find_critical_points)
        clear_btn.clicked.connect(lambda: self.graph_canvas.clear_points())
        
        btn_layout.addWidget(zeros_btn)
        btn_layout.addWidget(intersect_btn)
        btn_layout.addWidget(critical_btn)
        btn_layout.addWidget(clear_btn)
        analysis_layout.addLayout(btn_layout)
        
        # Results display
        self.analysis_result = QLabel("")
        analysis_layout.addWidget(self.analysis_result)
        
        analysis_group.setLayout(analysis_layout)
        controls.addWidget(analysis_group)
        
        self.graphing_layout.addLayout(controls)
        
        # Add the plotting canvas
        self.graph_canvas = graphing.GraphCanvas(self)
        self.graphing_layout.addWidget(self.graph_canvas)

    def plot_function(self):
        """Plot the current function"""
        expr = self.func_input.text().strip()
        if expr:
            self.graph_calc.add_function(expr)
            self.graph_canvas.plot_function(expr)
    
    def clear_plot(self):
        """Clear all plotted functions"""
        self.graph_calc.clear_functions()
        self.func_input.clear()
        self.graph_canvas.setup_axes()
        self.graph_canvas.draw()
    
    def update_window(self):
        """Update the plotting window ranges"""
        try:
            values = {name: float(inp.text())
                     for name, inp in self.window_inputs.items()}
            self.graph_canvas.set_window(**values)
            
            # Replot all active functions
            self.graph_canvas.setup_axes()
            for func in self.graph_calc.get_functions():
                self.graph_canvas.plot_function(func)
        except ValueError:
            pass  # Invalid number format - ignore
            
    def zoom_graph(self, factor):
        """Zoom in or out by the given factor"""
        try:
            # Get current window values
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            ymin = float(self.window_inputs['ymin'].text())
            ymax = float(self.window_inputs['ymax'].text())
            
            # Calculate center points
            xcenter = (xmax + xmin) / 2
            ycenter = (ymax + ymin) / 2
            
            # Calculate new ranges
            xrange = (xmax - xmin) / factor
            yrange = (ymax - ymin) / factor
            
            # Update window inputs
            self.window_inputs['xmin'].setText(f"{xcenter - xrange/2:.2f}")
            self.window_inputs['xmax'].setText(f"{xcenter + xrange/2:.2f}")
            self.window_inputs['ymin'].setText(f"{ycenter - yrange/2:.2f}")
            self.window_inputs['ymax'].setText(f"{ycenter + yrange/2:.2f}")
            
            # Update the window
            self.update_window()
        except ValueError:
            pass  # Invalid number format - ignore
            
    def reset_graph_view(self):
        """Reset to standard window (-10,10) x (-10,10)"""
        self.window_inputs['xmin'].setText("-10")
        self.window_inputs['xmax'].setText("10")
        self.window_inputs['ymin'].setText("-10")
        self.window_inputs['ymax'].setText("10")
        self.window_inputs['xscl'].setText("1")
        self.window_inputs['yscl'].setText("1")
        self.update_window()
        
    def trace_point(self):
        """Trace a point on the current function"""
        try:
            x = float(self.trace_x.text())
            expr = self.func_input.text().strip()
            
            if expr:
                y = self.graph_canvas.trace_function(expr, x)
                if y is not None:
                    self.graph_canvas.plot_point(x, y)
                    self.analysis_result.setText(f"Point: ({x:.3f}, {y:.3f})")
                else:
                    self.analysis_result.setText("Could not evaluate function at this point")
        except ValueError:
            self.analysis_result.setText("Invalid x value")
            
    def find_zeros(self):
        """Find x-intercepts of the current function"""
        expr = self.func_input.text().strip()
        if not expr:
            return
            
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            zeros = self.graph_calc.find_zeros(expr, xmin, xmax)
            
            if zeros:
                # Plot zeros
                for x in zeros:
                    self.graph_canvas.plot_point(x, 0, color='green')
                # Display results
                zeros_str = ", ".join(f"x = {x:.3f}" for x in zeros)
                self.analysis_result.setText(f"Zeros found: {zeros_str}")
            else:
                self.analysis_result.setText("No zeros found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding zeros: {str(e)}")
            
    def find_intersections(self):
        """Find intersections between two functions"""
        try:
            expr1 = self.func_input.text().strip()
            if not expr1:
                self.analysis_result.setText("Enter first function")
                return
                
            expr2, ok = QInputDialog.getText(self, 
                "Find Intersections",
                "Enter second function:")
            
            if ok and expr2:
                xmin = float(self.window_inputs['xmin'].text())
                xmax = float(self.window_inputs['xmax'].text())
                points = self.graph_calc.find_intersections(expr1, expr2, xmin, xmax)
                
                if points:
                    # Plot intersection points
                    for x, y in points:
                        self.graph_canvas.plot_point(x, y, color='blue')
                    # Display results
                    points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                    self.analysis_result.setText(f"Intersections: {points_str}")
                else:
                    self.analysis_result.setText("No intersections found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding intersections: {str(e)}")
            
    def find_critical_points(self):
        """Find local maxima and minima"""
        expr = self.func_input.text().strip()
        if not expr:
            return
            
        try:
            xmin = float(self.window_inputs['xmin'].text())
            xmax = float(self.window_inputs['xmax'].text())
            points = self.graph_calc.find_critical_points(expr, xmin, xmax)
            
            if points:
                # Plot critical points
                for x, y in points:
                    self.graph_canvas.plot_point(x, y, color='purple')
                # Display results
                points_str = ", ".join(f"({x:.3f}, {y:.3f})" for x, y in points)
                self.analysis_result.setText(f"Critical points: {points_str}")
            else:
                self.analysis_result.setText("No critical points found in current window")
        except Exception as e:
            self.analysis_result.setText(f"Error finding critical points: {str(e)}")

    def set_styles(self):
        """Initialize with dark theme by default"""
        self.current_theme = 'dark'
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current theme"""
        try:
            theme_file = Path(__file__).parent / 'styles' / 'themes' / f'{self.current_theme}.qss'
            if theme_file.exists():
                self.setStyleSheet(theme_file.read_text())
                
                # Update button text
                if self.current_theme == 'dark':
                    self.theme_btn.setText("☀️ Light Mode")
                else:
                    self.theme_btn.setText("🌙 Dark Mode")
        except Exception:
            # fallback: a minimal inline style
            self.setStyleSheet('QWidget { background: #2b3136 }')
            
    def toggle_theme(self):
        """Switch between light and dark themes"""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()


def run_app():
    app = QApplication(sys.argv)
    w = CalculatorGUI()
    w.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(run_app())
