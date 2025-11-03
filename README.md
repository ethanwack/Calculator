# PyQt5 Calculator

A feature-rich calculator application built with Python and PyQt5, inspired by the TI-84 calculator. It includes basic arithmetic, scientific functions, and graphing capabilities.

## Features

### Basic Calculator
- Standard arithmetic operations (+, -, ×, ÷)
- Memory functions (MC, MR, M+, M-)
- Common mathematical constants (π, e)
- Basic functions (√, x², 1/x, %)

### Scientific Calculator
- Trigonometric functions (sin, cos, tan)
- Inverse trig functions (asin, acos, atan)
- Hyperbolic functions (sinh, cosh, tanh)
- Logarithms (log, ln)
- Advanced operations (x^y, |x|, ⌊x⌋, ⌈x⌉)
- Combinatorics (nPr, nCr)
- Degree/Radian modes

### Graphing Calculator
- Function plotting (similar to TI-84)
- Adjustable window settings
- Grid and axes display
- Support for common math functions
- Multiple function plots

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/Calculator.git
cd Calculator
```

2. (Optional) Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

Run the calculator:
```bash
python Main.py
```

### Graphing Functions
1. Switch to the "Graph" tab
2. Enter a function in the Y= input (e.g., x^2, sin(x), 2*x+1)
3. Click "Plot" to display the function
4. Adjust window settings as needed
5. Use "Clear" to reset the graph

## Project Structure
- `Main.py` — Application entry point
- `calculator/`
  - `gui.py` — PyQt5 GUI implementation
  - `core.py` — Core mathematical operations
  - `graphing.py` — Graphing functionality
  - `styles/` — QSS style sheets for theming

## Dependencies
- PyQt5 - GUI framework
- numpy - Numerical computations
- scipy - Scientific computations
- matplotlib - Plotting functionality

## Contributing
Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License
This project is open source and available under the MIT License.
