"""Launcher for calculator GUI (cleaned)."""
import sys

from calculator.gui import run_app


if __name__ == '__main__':
    sys.exit(run_app())
"""Launcher for calculator GUI (cleaned).

This file is a minimal entrypoint that uses the clean GUI implementation
from `calculator.gui` (which re-exports the working code from
`calculator.gui_new`).
"""