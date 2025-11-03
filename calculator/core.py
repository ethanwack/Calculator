"""
Core math helpers for the calculator.
This keeps computation separate from the UI.
"""
import math

def to_number(s):
    try:
        return float(s)
    except Exception:
        raise ValueError("Invalid number")

def format_result(v):
    try:
        fv = float(v)
        if math.isfinite(fv) and fv.is_integer():
            return str(int(fv))
        # limit to reasonable precision
        return f"{fv:.10g}"
    except Exception:
        return str(v)

def safe_add(a, b):
    return a + b

def safe_sub(a, b):
    return a - b

def safe_mul(a, b):
    return a * b

def safe_div(a, b):
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

def power(a, b):
    return math.pow(a, b)

def factorial(n):
    n_int = int(n)
    if n_int < 0:
        raise ValueError("factorial of negative number")
    return math.factorial(n_int)

def nPr(n, r):
    n_int = int(n)
    r_int = int(r)
    if r_int < 0 or n_int < 0 or r_int > n_int:
        raise ValueError("invalid nPr params")
    return math.perm(n_int, r_int)

def nCr(n, r):
    n_int = int(n)
    r_int = int(r)
    if r_int < 0 or n_int < 0 or r_int > n_int:
        raise ValueError("invalid nCr params")
    return math.comb(n_int, r_int)

def deg_to_rad(x):
    return math.radians(x)

def rad_to_deg(x):
    return math.degrees(x)
