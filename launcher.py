"""Launcher for calculator GUI (cleaned).

This is a minimal, atomic launcher that imports the clean GUI
implementation from `calculator.gui_new` to avoid any corrupted files.
"""
import sys

from calculator.gui_new import run_app


if __name__ == '__main__':
    sys.exit(run_app())
