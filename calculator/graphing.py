"""
Graphing functionality similar to TI-84 calculators.
Handles function plotting and window management.
"""
import re
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class GraphCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        
        # TI-84 like default window
        self.xmin = -10
        self.xmax = 10
        self.ymin = -10
        self.ymax = 10
        self.xscl = 1
        self.yscl = 1
        
        # Pan tracking
        self._pan_start = None
        
        self.setup_axes()
    
    def setup_axes(self):
        """Configure axes with grid and ranges"""
        self.axes.clear()
        self.axes.grid(True)
        self.axes.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        self.axes.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
        self.axes.set_xlim(self.xmin, self.xmax)
        self.axes.set_ylim(self.ymin, self.ymax)
        # Set major ticks according to scale
        self.axes.set_xticks(np.arange(self.xmin, self.xmax + 1, self.xscl))
        self.axes.set_yticks(np.arange(self.ymin, self.ymax + 1, self.yscl))
        
        # Enable mouse pan and zoom
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        # Store initial view for reset
        self._default_xlim = (self.xmin, self.xmax)
        self._default_ylim = (self.ymin, self.ymax)
    
    def set_window(self, xmin, xmax, ymin, ymax, xscl=1, yscl=1):
        """Update window ranges and redraw"""
        self.xmin = float(xmin)
        self.xmax = float(xmax)
        self.ymin = float(ymin)
        self.ymax = float(ymax)
        self.xscl = float(xscl)
        self.yscl = float(yscl)
        self.setup_axes()
        self.draw()
    
    def plot_function(self, expr):
        """Plot a mathematical expression"""
        try:
            # Create x points for smooth plotting
            x = np.linspace(self.xmin, self.xmax, 500)
            
            # Convert the expression to numpy-compatible form
            expr = self.prepare_expression(expr)
            
            # Evaluate using numpy
            y = eval(expr)
            
            # Plot and refresh
            self.axes.plot(x, y)
            self.draw()
            return True
        except Exception as e:
            print(f"Error plotting: {e}")
            return False
    
    def prepare_expression(self, expr):
        """Convert a TI-84 style expression to numpy form"""
        # Replace common mathematical operations
        expr = expr.lower()
        expr = re.sub(r'\^', '**', expr)  # power
        expr = re.sub(r'sin\(', 'np.sin(', expr)
        expr = re.sub(r'cos\(', 'np.cos(', expr)
        expr = re.sub(r'tan\(', 'np.tan(', expr)
        expr = re.sub(r'log\(', 'np.log10(', expr)
        expr = re.sub(r'ln\(', 'np.log(', expr)
        expr = re.sub(r'sqrt\(', 'np.sqrt(', expr)
        expr = re.sub(r'abs\(', 'np.abs(', expr)
        expr = re.sub(r'pi\b', 'np.pi', expr)
        expr = re.sub(r'e\b', 'np.e', expr)
        
        # Ensure multiplication is explicit (2x -> 2*x)
        expr = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', expr)
        
        return expr.replace('x', '(x)')
        
    def reset_view(self):
        """Reset to default window settings"""
        if hasattr(self, '_default_xlim') and hasattr(self, '_default_ylim'):
            self.xmin, self.xmax = self._default_xlim
            self.ymin, self.ymax = self._default_ylim
            self.setup_axes()
            self.draw()
            
    def on_mouse_press(self, event):
        """Handle mouse button press"""
        if event.inaxes != self.axes:
            return
        self._pan_start = (event.xdata, event.ydata)
        
    def on_mouse_release(self, event):
        """Handle mouse button release"""
        self._pan_start = None
        
    def on_mouse_move(self, event):
        """Handle mouse movement for panning"""
        if event.inaxes != self.axes or self._pan_start is None or not event.button:
            return
        
        # Calculate the distance moved
        dx = event.xdata - self._pan_start[0]
        dy = event.ydata - self._pan_start[1]
        
        # Update limits
        self.axes.set_xlim(self.axes.get_xlim() - dx)
        self.axes.set_ylim(self.axes.get_ylim() - dy)
        
        # Update internal values
        self.xmin, self.xmax = self.axes.get_xlim()
        self.ymin, self.ymax = self.axes.get_ylim()
        
        self.draw()
        
    def on_scroll(self, event):
        """Handle mouse wheel for zooming"""
        if event.inaxes != self.axes:
            return
            
        # Get the current pointer position
        xdata, ydata = event.xdata, event.ydata
        
        # Get current axis ranges
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        
        # Get the relative position of the mouse
        x_rel = (xdata - cur_xlim[0]) / (cur_xlim[1] - cur_xlim[0])
        y_rel = (ydata - cur_ylim[0]) / (cur_ylim[1] - cur_ylim[0])
        
        # Zoom factor 1.2 or 1/1.2
        scale_factor = 1.2 if event.button == 'up' else 1/1.2
        
        # Calculate new ranges
        x_range = (cur_xlim[1] - cur_xlim[0]) / scale_factor
        y_range = (cur_ylim[1] - cur_ylim[0]) / scale_factor
        
        # Calculate new limits
        self.xmin = xdata - x_rel * x_range
        self.xmax = self.xmin + x_range
        self.ymin = ydata - y_rel * y_range
        self.ymax = self.ymin + y_range
        
        # Update plot
        self.setup_axes()
        self.draw()  # wrap x in parentheses for safety


class GraphingCalculator:
    """Main graphing interface"""
    def __init__(self):
        self.functions = []  # Store active functions
        self.current_function = ""
        
    def set_function(self, expr):
        """Set the current function to plot"""
        self.current_function = expr
        
    def add_function(self, expr):
        """Add a function to the plot"""
        if expr and expr not in self.functions:
            self.functions.append(expr)
            return True
        return False
        
    def clear_functions(self):
        """Clear all plotted functions"""
        self.functions = []
        self.current_function = ""
        
    def get_functions(self):
        """Get list of active functions"""
        return self.functions.copy()