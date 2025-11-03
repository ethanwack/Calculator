"""Launcher for calculator GUI (now split into package)."""
import sys

from calculator.gui import run_app


if __name__ == '__main__':
    sys.exit(run_app())
    
    def set_theme(self):
        style = """
            QMainWindow, QWidget {
                background-color: #34495E;
            }
            
            QTabWidget::pane {
                border: none;
                background-color: #34495E;
            }
            
            QTabBar::tab {
                background-color: #2C3E50;
                color: white;
                min-width: 100px;
                padding: 10px;
                border-radius: 5px 5px 0 0;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #3498DB;
            }
            
            QLabel#display {
                background-color: #2C3E50;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-size: 24pt;
                min-height: 60px;
                margin: 5px;
            }
            
            QPushButton {
                background-color: #455A64;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
                font-size: 14pt;
                min-width: 50px;
                min-height: 50px;
            }
            
            QPushButton:hover {
                background-color: #546E7A;
            }
            
            QPushButton[class="operator"] {
                background-color: #FF9800;
                font-weight: bold;
            }
            
            QPushButton[class="operator"]:hover {
                background-color: #FFA726;
            }
            
            QPushButton[class="equals"] {
                background-color: #2196F3;
                font-weight: bold;
            }
            
            QPushButton[class="equals"]:hover {
                background-color: #42A5F5;
            }
            
            QPushButton[class="clear"] {
                background-color: #F44336;
                font-weight: bold;
            }
            
            QPushButton[class="clear"]:hover {
                background-color: #EF5350;
            }
            
            QPushButton[class="function"] {
                background-color: #673AB7;
            }
            
            QPushButton[class="function"]:hover {
                background-color: #7E57C2;
            }
            
            QPushButton[class="memory"] {
                background-color: #009688;
            }
            
            QPushButton[class="memory"]:hover {
                background-color: #26A69A;
            }
            
            QPushButton[class="mode"] {
                background-color: #795548;
            }
            
            QPushButton[class="mode"]:hover {
                background-color: #8D6E63;
            }
        """
        self.setStyleSheet(style)
    
    def create_display(self, layout):
        self.display = QLabel("0")
        self.display.setObjectName("display")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.display)

    def create_button(self, text, button_class=None):
        button = QPushButton(text)
        if button_class:
            button.setProperty('class', button_class)
        button.clicked.connect(lambda checked, t=text: self.button_click(t))
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return button

    def create_basic_buttons(self, layout):
        buttons_layout = QGridLayout()
        
        # Button layout
        button_layout = [
            ('MC', 'MR', 'M+', 'M-', 'C'),
            ('±', '√', '%', '÷', '←'),
            ('7', '8', '9', '×', 'x²'),
            ('4', '5', '6', '-', '1/x'),
            ('1', '2', '3', '+', '='),
            ('0', '.', 'π', 'e')
        ]
        
        # Create buttons
        for i, row in enumerate(button_layout):
            for j, text in enumerate(row):
                # Determine button class
                button_class = None
                if text in '+-×÷':
                    button_class = 'operator'
                elif text == '=':
                    button_class = 'equals'
                elif text == 'C':
                    button_class = 'clear'
                elif text in ('MC', 'MR', 'M+', 'M-'):
                    button_class = 'memory'
                elif text in ('√', '%', 'x²', '1/x', 'π', 'e'):
                    button_class = 'function'
                
                button = self.create_button(text, button_class)
                
                # Handle special cases for button placement
                if text == '=':
                    buttons_layout.addWidget(button, i-1, j, 2, 1)
                elif text == '0':
                    buttons_layout.addWidget(button, i, j, 1, 2)
                else:
                    buttons_layout.addWidget(button, i, j)
        
        layout.addLayout(buttons_layout)

    def create_scientific_buttons(self, layout):
        buttons_layout = QGridLayout()
        
        # Button layout for scientific calculator
        button_layout = [
            ('DEG', 'RAD', 'INV', 'log', 'ln'),
            ('sin', 'cos', 'tan', '(', ')'),
            ('asin', 'acos', 'atan', 'x^y', '|x|'),
            ('sinh', 'cosh', 'tanh', '⌊x⌋', '⌈x⌉'),
            ('nPr', 'nCr', 'x!', 'rand', 'EE'),
            ('7', '8', '9', '÷', '←'),
            ('4', '5', '6', '×', 'C'),
            ('1', '2', '3', '-', '='),
            ('0', '.', 'π', '+')
        ]
        
        # Create buttons
        for i, row in enumerate(button_layout):
            for j, text in enumerate(row):
                # Determine button class
                button_class = None
                if text in '+-×÷':
                    button_class = 'operator'
                elif text == '=':
                    button_class = 'equals'
                elif text == 'C':
                    button_class = 'clear'
                elif text in ('DEG', 'RAD', 'INV'):
                    button_class = 'mode'
                elif not text.isdigit() and text not in ('.',):
                    button_class = 'function'
                
                button = self.create_button(text, button_class)
                
                # Handle special cases for button placement
                if text == '=':
                    buttons_layout.addWidget(button, i-1, j, 2, 1)
                elif text == '0':
                    buttons_layout.addWidget(button, i, j, 1, 2)
                else:
                    buttons_layout.addWidget(button, i, j)
        
        layout.addLayout(buttons_layout)
    
    def button_click(self, value):
        try:
            if value.isdigit():
                if self.should_reset:
                    self.current_number = value
                    self.should_reset = False
                else:
                    self.current_number = self.current_number if self.current_number != "0" else ""
                    self.current_number += value
            
            elif value == '.':
                if '.' not in self.current_number:
                    self.current_number += value
            
            elif value in ('π', 'e'):
                self.current_number = str(math.pi if value == 'π' else math.e)
                self.should_reset = True
            
            elif value == '←':
                self.current_number = self.current_number[:-1] if len(self.current_number) > 1 else "0"
            
            elif value in ('C', 'CE'):
                self.clear()
            
            elif value == '±':
                self.toggle_sign()
            
            elif value == '%':
                self.percentage()
            
            elif value in ('MC', 'MR', 'M+', 'M-'):
                self.handle_memory(value)
            
            elif value in ('DEG', 'RAD'):
                self.angle_mode = value
                self.update_display()
                return
            
            elif value == 'INV':
                self.inverse_mode = not self.inverse_mode
                self.update_display()
                return
            
            elif value in ('sin', 'cos', 'tan', 'asin', 'acos', 'atan', 
                          'sinh', 'cosh', 'tanh'):
                self.handle_trig(value)
            
            elif value == 'x²':
                self.square()
            
            elif value == '√':
                self.sqrt()
            
            elif value == '1/x':
                self.reciprocal()
            
            elif value == 'x^y':
                self.handle_operator('^')
            
            elif value == '|x|':
                self.abs()
            
            elif value in ('⌊x⌋', '⌈x⌉'):
                self.handle_floor_ceil(value)
            
            elif value in ('log', 'ln'):
                self.handle_log(value)
            
            elif value == 'x!':
                self.factorial()
            
            elif value in ('nPr', 'nCr'):
                self.handle_operator(value)
            
            elif value == 'rand':
                self.current_number = str(np.random.random())
            
            elif value == 'EE':
                if self.current_number != "0":
                    self.current_number += "e"
            
            elif value in '+-×÷^':
                self.handle_operator(value)
            
            elif value == '=':
                self.calculate()
            
            self.update_display()
        
        except Exception as e:
            self.current_number = "Error"
            self.update_display()
    
    def handle_trig(self, func):
        try:
            x = float(self.current_number)
            if self.angle_mode == "DEG":
                x = math.radians(x)
            
            if func in ('sin', 'cos', 'tan'):
                if self.inverse_mode:
                    result = getattr(math, 'a' + func)(x)
                    if self.angle_mode == "DEG":
                        result = math.degrees(result)
                else:
                    result = getattr(math, func)(x)
            else:  # hyperbolic functions
                result = getattr(math, func)(x)
            
            self.current_number = str(result)
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def handle_floor_ceil(self, func):
        try:
            x = float(self.current_number)
            if func == '⌊x⌋':
                result = math.floor(x)
            else:
                result = math.ceil(x)
            self.current_number = str(result)
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def handle_log(self, func):
        try:
            x = float(self.current_number)
            if func == 'log':
                result = math.log10(x)
            else:  # ln
                result = math.log(x)
            self.current_number = str(result)
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def factorial(self):
        try:
            x = int(float(self.current_number))
            if x < 0:
                raise ValueError("Factorial of negative number")
            result = math.factorial(x)
            self.current_number = str(result)
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def square(self):
        try:
            x = float(self.current_number)
            self.current_number = str(x * x)
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def sqrt(self):
        try:
            x = float(self.current_number)
            if x < 0:
                raise ValueError("Square root of negative number")
            self.current_number = str(math.sqrt(x))
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def reciprocal(self):
        try:
            x = float(self.current_number)
            if x == 0:
                raise ValueError("Division by zero")
            self.current_number = str(1 / x)
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def abs(self):
        try:
            x = float(self.current_number)
            self.current_number = str(abs(x))
            self.should_reset = True
        except Exception:
            self.current_number = "Error"
    
    def handle_memory(self, operation):
        try:
            if operation == 'MC':
                self.memory = 0
            elif operation == 'MR':
                self.current_number = str(self.memory)
                self.should_reset = True
            elif operation == 'M+':
                self.memory += float(self.current_number)
            elif operation == 'M-':
                self.memory -= float(self.current_number)
        except Exception:
            self.current_number = "Error"
    
    def clear(self):
        self.current_number = "0"
        self.operation = None
        self.last_number = None
        self.should_reset = False
    
    def toggle_sign(self):
        if self.current_number != "0":
            if self.current_number[0] == '-':
                self.current_number = self.current_number[1:]
            else:
                self.current_number = '-' + self.current_number
    
    def percentage(self):
        try:
            value = float(self.current_number)
            self.current_number = str(value / 100)
        except ValueError:
            self.current_number = "Error"
    
    def handle_operator(self, op):
        if self.last_number is not None:
            self.calculate()
        self.last_number = float(self.current_number)
        self.operation = op
        self.should_reset = True
    
    def calculate(self):
        if self.operation and self.last_number is not None:
            try:
                current = float(self.current_number)
                result = None
                
                if self.operation == '+':
                    result = self.last_number + current
                elif self.operation == '-':
                    result = self.last_number - current
                elif self.operation == '×':
                    result = self.last_number * current
                elif self.operation == '÷':
                    if current == 0:
                        raise ValueError("Division by zero")
                    result = self.last_number / current
                elif self.operation == '^':
                    result = math.pow(self.last_number, current)
                elif self.operation == 'nPr':
                    n = int(self.last_number)
                    r = int(current)
                    if n < 0 or r < 0 or r > n:
                        raise ValueError("Invalid permutation parameters")
                    result = math.perm(n, r)
                elif self.operation == 'nCr':
                    n = int(self.last_number)
                    r = int(current)
                    if n < 0 or r < 0 or r > n:
                        raise ValueError("Invalid combination parameters")
                    result = math.comb(n, r)
                
                # Format result to avoid floating point precision issues
                if result is not None:
                    if float(result).is_integer():
                        self.current_number = str(int(result))
                    else:
                        self.current_number = f"{result:.8f}".rstrip('0').rstrip('.')
                
                self.last_number = None
                self.operation = None
                self.should_reset = True
                
            except Exception as e:
                self.current_number = "Error"
    
    def update_display(self):
        self.display.setText(self.current_number)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = CalculatorGUI()
    calculator.show()
    sys.exit(app.exec_())