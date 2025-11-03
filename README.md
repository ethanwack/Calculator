# Calculator

This project is a Python GUI calculator (basic + scientific). It uses PyQt5 for the UI and a small `calculator` package to separate UI and logic.

How to run

1. (Optional) Create and activate a virtual environment.
2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python Main.py
```

Files

- `Main.py` — launcher (imports calculator.gui)
- `calculator/gui.py` — PyQt5 GUI and event wiring
- `calculator/core.py` — math helpers

If any buttons still behave unexpectedly, open `calculator/gui.py` and check `create_basic_grid` and `button_click` for the handling logic.
