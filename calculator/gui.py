"""
GUI for the calculator. Uses PyQt5. Keeps UI concerns separate from core logic.
"""
import sys
import math
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QTabWidget, QSizePolicy, QLineEdit,
    QHBoxLayout, QGroupBox, QFormLayout
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

        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Basic tab
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        self.basic_display = QLabel("0")
        self.basic_display.setObjectName("display")
        self.basic_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.basic_display.setFont(QFont('Consolas', 24))
        self.basic_layout.addWidget(self.basic_display)
        self.create_basic_grid(self.basic_layout)
        self.tabs.addTab(self.basic_tab, "Basic")

        # Scientific tab
        self.scientific_tab = QWidget()
        self.scientific_layout = QVBoxLayout(self.scientific_tab)
        self.scientific_display = QLabel("0")
        self.scientific_display.setObjectName("display")
        self.scientific_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scientific_display.setFont(QFont('Consolas', 20))
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
            ('MC','MR','M+','M-','C'),
            ('±','√','%','÷','←'),
            ('7','8','9','×','x²'),
            ('4','5','6','-','1/x'),
            ('1','2','3','+','='),
            ('0','0','.','π','e')
        ]

        for r, row in enumerate(labels):
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
        window_group.setLayout(window_layout)
        controls.addWidget(window_group)
        
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

    def set_styles(self):
        """Load and apply .qss files from the styles folder (if present).
        The files are applied in this order to allow overrides:
        base.qss, display.qss, buttons.qss, tabs.qss
        """
        try:
            style_dir = Path(__file__).parent / 'styles'
            parts = []
            for name in ('base.qss', 'display.qss', 'buttons.qss', 'tabs.qss'):
                p = style_dir / name
                if p.exists():
                    parts.append(p.read_text())
            if parts:
                self.setStyleSheet('\n'.join(parts))
        except Exception:
            # fallback: a minimal inline style
            self.setStyleSheet('QWidget { background: #2b3136 }')


def run_app():
    app = QApplication(sys.argv)
    w = CalculatorGUI()
    w.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(run_app())
