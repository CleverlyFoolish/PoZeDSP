# This module handles string manipulation, LaTeX formatting for plots, 
# and parsing of complex number strings from user inputs.
# It is used primarily by the UI components to display equations and process text fields.

# -----------------------------------------------------------------------------
# Copyright (C) 2026 Rishabh Shetty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See <https://www.gnu.org/licenses/>.
# =============================================================================

import re

# ------------------------------------------------------------
# Text & LaTeX Formatting
# ------------------------------------------------------------

def fmt_coeff(c):
    """
    Formats a complex number into a clean string representation.
    """
    if abs(c.imag) < 1e-12:
        return f"{c.real:.2f}"
    op = "+" if c.imag >= 0 else "-"
    return f"({c.real:.2f} {op} {abs(c.imag):.2f}j)"

def poly_to_mathtext(c):
    """
    Converts a list of polynomial coefficients into a LaTeX-formatted 
    z-transform string.
    """
    terms = []
    for k, v in enumerate(c):
        if abs(v) < 1e-12:
            continue
        coeff = fmt_coeff(v)
        if k == 0:
            terms.append(coeff)
        else:
            terms.append(rf"{coeff}z^{{-{k}}}")
    return " + ".join(terms) if terms else "0"

def format_latex_title(expr):
    """
    Converts a Python numpy expression string (e.g. 'np.sin(0.1*n)') 
    into a LaTeX string for plot titles.
    """
    # 1. Basic Cleanups
    tex = expr.replace('np.', '') 
    tex = tex.replace('*', r' \cdot ')
    
    # 2. Replace 'pi' -> '\pi' (Use regex to match whole word 'pi' only)
    # This prevents replacing the 'pi' inside 'exp' or '\pi' itself
    tex = re.sub(r'\bpi\b', r'\\pi', tex)

    # 3. Replace functions (sin, cos, etc.)
    # We use \b to ensure we match 'sin' but not 'sinc' or '\sin'
    funcs = ['sin', 'cos', 'tan', 'exp', 'log', 'sinc', 'sqrt']
    for func in funcs:
        # Replace 'func' with '\func'
        tex = re.sub(rf'\b{func}\b', rf'\\{func}', tex)

    # 4. Special cases for u(n) and delta(n)
    # Replace 'u(' with 'u(' (no change needed usually, or \text{u})
    # Replace 'd(' or 'delta(' or 'impulse(' with '\delta('
    tex = re.sub(r'\b(d|delta|impulse)\(', r'\\delta(', tex)
    
    # Correction for double backslash if any crept in
    tex = tex.replace(r'\\\sin', r'\sin') 
    
    return f"${tex}$" 

# ------------------------------------------------------------
# Input Parsing
# ------------------------------------------------------------

def parse_complex_list(text):
    """
    Parses a comma-separated string of complex numbers.
    """
    if not text.strip(): return []
    
    parts = text.split(',')
    clean_nums = []
    for p in parts:
        p = p.strip().replace('(', '').replace(')', '').replace(' ', '')
        if not p: continue
        try:
            clean_nums.append(complex(p))
        except ValueError:
            try:
                clean_nums.append(complex(float(p)))
            except ValueError:
                pass
                
    return clean_nums