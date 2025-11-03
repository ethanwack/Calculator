"""
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
