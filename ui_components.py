# This module contains the custom UI widgets and dialogs for the PoZeDSP tool.
# It includes the advanced textbox logic, button styling, signal analysis popup,
# and the Transfer Function editor dialog.

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

# Note: tkinter imports moved inside functions for macOS compatibility
# import tkinter as tk
# from tkinter import simpledialog, messagebox
import numpy as np
import matplotlib.pyplot as plt

# Internal Modules
import state_manager as sm
import dsp_engine as dsp
import formatting_utils as fmt

# ------------------------------------------------------------
# Custom Widget Logic
# ------------------------------------------------------------

def setup_advanced_textbox(textbox, tk_root):
    """
    Enhances a Matplotlib TextBox with clipboard support (Ctrl+C/V),
<<<<<<< HEAD
    Select All (Ctrl+A), and auto-scroll alignment.
    Note: Some features disabled when tk_root is None.
=======
    Select All (Ctrl+A), and smart scrolling that tracks the cursor.
>>>>>>> main
    """
    # Enhanced textbox logic enabled
    textbox._select_all_mode = False
        
    textbox._select_all_mode = False

    def update_view(event=None):
        """
        Smart scrolling: Shifts the text horizontally so the area 
        around the cursor is always visible.
        """
        # 1. Get Text Dimensions
        txt_obj = textbox.text_disp
        renderer = textbox.ax.figure.canvas.get_renderer()
        
        # Get the bounding box of the text content
        bbox = txt_obj.get_window_extent(renderer)
        text_width = bbox.width
        
        # Get the width of the textbox container (axis)
        box_bbox = textbox.ax.get_window_extent(renderer)
        box_width = box_bbox.width

        # 2. Calculate Overflow
        overflow = text_width - box_width
        
        # Default Alignment (Left, with small padding)
        base_x = 0.05
        align = 'left'
        
        # 3. Apply Scroll if needed
        if overflow > 0 and len(textbox.text) > 0:
            cursor_ratio = textbox.cursor_index / len(textbox.text)
            cursor_ratio = max(0.0, min(1.0, cursor_ratio))
            
            # We add a small buffer so the cursor isn't glued to the edge.
            shift_pixels = -1 * cursor_ratio * (overflow + 20) # +20px buffer
            new_x = base_x + (shift_pixels / box_width)
            
            # Apply
            txt_obj.set_horizontalalignment(align)
            txt_obj.set_x(new_x)
            
        else:
            # Text fits? Reset to standard Left alignment
            txt_obj.set_horizontalalignment(align)
            txt_obj.set_x(base_x)

        textbox.ax.figure.canvas.draw_idle()

    def on_key_press(event):
        if event.inaxes != textbox.ax:
            return

        # --- 1. Handle Ctrl+A (Select All) ---
        if event.key == 'ctrl+a':
            textbox._select_all_mode = True
            textbox.text_disp.set_color('blue')
            textbox.ax.figure.canvas.draw_idle()
            return

        # --- 2. Handle Backspace ---
        if event.key == 'backspace':
            if textbox._select_all_mode:
                textbox.set_val("")
                textbox._select_all_mode = False
                textbox.text_disp.set_color('black')
            else:
                pass 

        # --- 3. Handle Copy (Ctrl+C) ---
        elif event.key == 'ctrl+c':
            tk_root.clipboard_clear()
            tk_root.clipboard_append(textbox.text)
            tk_root.update()

        # --- 4. Handle Paste (Ctrl+V) ---
        elif event.key == 'ctrl+v':
            try:
                paste_text = tk_root.clipboard_get()
                current_text = textbox.text
                if textbox._select_all_mode:
                    new_text = paste_text
                else:
                    c_idx = textbox.cursor_index
                    new_text = current_text[:c_idx] + paste_text + current_text[c_idx:]
                
                textbox.set_val(new_text)
                textbox._select_all_mode = False
                textbox.text_disp.set_color('black')
            except Exception:
                pass

        # --- 5. Handle Normal Typing ---
        elif len(event.key) == 1 and not event.key.startswith('ctrl'):
            if textbox._select_all_mode:
                textbox.set_val(event.key)
                textbox._select_all_mode = False
                textbox.text_disp.set_color('black')

        update_view()

    # Connect the event
    textbox.ax.figure.canvas.mpl_connect('key_press_event', on_key_press)
    
    # Also update view on any text content change
    textbox.on_text_change(lambda x: update_view())

def decorate_button(ax, type_):
    """
    Draws custom icons (Zero circle / Pole X) on the toolbar buttons.
    """
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    if type_ == 'zero':
        # Blue Circle
        ax.plot(0.5, 0.55, 'o', color='blue', markeredgewidth=2, 
                markersize=18, markerfacecolor='none', label='Zero')
        ax.text(0.5, 0.25, "Add Zero", ha='center', va='top', fontsize=9, fontweight='bold')
    elif type_ == 'pole':
        # Red X
        ax.plot(0.5, 0.55, 'x', color='red', markeredgewidth=3, 
                markersize=18, label='Pole')
        ax.text(0.5, 0.25, "Add Pole", ha='center', va='top', fontsize=9, fontweight='bold')

# ------------------------------------------------------------
# Popups and Dialogs
# ------------------------------------------------------------

def show_signal_analysis(event=None):
    """
    Opens a separate Matplotlib figure to simulate filtering a custom signal.
    """
    txt_n = getattr(sm, 'txt_n', None)
    txt_sig = getattr(sm, 'txt_sig', None)

    if not txt_n or not txt_sig:
        return

    try:
        num_pts = int(txt_n.text)
    except:
        num_pts = 200
    n_array = np.arange(num_pts)

    try:
        expr = txt_sig.text
        
        math_env = {
            'n': n_array,
            'np': np,
            'random': np.random,
            'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
            'exp': np.exp, 'pi': np.pi, 'sqrt': np.sqrt,
            'log': np.log10, 'ln': np.log, 'abs': np.abs,
            'sum': np.sum, 'real': np.real, 'imag': np.imag, 'sign': np.sign,
            'u': dsp.unit_step,      
            'step': dsp.unit_step,   
            'd': dsp.impulse,        
            'delta': dsp.impulse,    
            'impulse': dsp.impulse,  
            'r': dsp.ramp,           
            'sinc': np.sinc,
            'rect': dsp.rect,        
            'len': len,
            'pulse_train': lambda start, space, num: dsp.pulse_train_gen(n_array, start, space, num),
            'pt': lambda start, space, num: dsp.pulse_train_gen(n_array, start, space, num)
        }

        x = eval(expr, {"__builtins__": None}, math_env)
        x = np.array(x, dtype=float)
        if x.ndim == 0: x = np.full(num_pts, x)
        
    except Exception as e:
        # Handle both signal processing errors and tkinter import errors
        try:
            import tkinter as tk
            from tkinter import messagebox
            tk.messagebox.showerror("Signal Error", f"Invalid Expression: {e}")
        except Exception:
            print(f"Signal Error: {e} (messagebox disabled)")
        return

    # Generate the LaTeX title safely
    latex_title = fmt.format_latex_title(txt_sig.text)
    
    b, a = dsp.coeffs_quantized()
    
    y = dsp.filter_signal(b, a, x)

    if sm.system_delay != 0:
        y = np.roll(y, sm.system_delay)
        if sm.system_delay > 0: y[:sm.system_delay] = 0
        else: y[sm.system_delay:] = 0

    if sm.signal_fig is None or not plt.fignum_exists(sm.signal_fig.number):
        sm.signal_fig = plt.figure("Signal Analysis", figsize=(9, 6))
    else:
        sm.signal_fig.clf()
    
    ax1 = sm.signal_fig.add_subplot(211)
    
    # FIX: Use a raw string format if possible, but the main fix is in formatting_utils.py
    # We remove the "Input Signal x[n]:" text from the math block to avoid parser confusion.
    ax1.set_title(f"Input Signal: {latex_title}", fontsize=12)
    
    ax1.plot(n_array, x, 'red', label='Input')
    ax1.grid(True, alpha=0.3); ax1.legend()

    ax2 = sm.signal_fig.add_subplot(212)
    ax2.set_title("Filtered Output y[n]")
    ax2.plot(n_array, y, 'b', linewidth=2, label='Output')
    ax2.plot(n_array, x, 'red', alpha=0.4, linestyle='--') 
    ax2.grid(True, alpha=0.3); ax2.legend()
    
    sm.signal_fig.tight_layout()
    sm.signal_fig.canvas.draw_idle()
    sm.signal_fig.show()

def open_tf_editor(event, tk_root, update_callback):
    """
    Opens a Tkinter dialog to manually edit the Transfer Function coefficients.
    """
        
    # Verify the click happened on the text box
    tf_text_artist = getattr(sm, 'tf_text_artist', None)
    if event.artist != tf_text_artist: 
        return

    import tkinter as tk
    dialog = tk.Toplevel(tk_root)
    dialog.title("Edit Transfer Function")
    dialog.geometry("400x250") 
    
    def add_row(label_text, default_val):
        frame = tk.Frame(dialog, pady=5)
        frame.pack(fill='x', padx=10)
        
        tk.Label(frame, text=label_text, width=18, anchor='w', font=("Arial", 10, "bold")).pack(side='left')
        
        entry = tk.Entry(frame)
        entry.insert(0, default_val)
        entry.pack(side='right', expand=True, fill='x')
        return entry

    # Get current coeffs for defaults
    curr_b, curr_a = dsp.coeffs_quantized()
    
    def arr_to_str(arr): return ", ".join([str(x) for x in arr])
    
    entry_b = add_row("Numerator (b):", arr_to_str(curr_b))
    entry_a = add_row("Denominator (a):", arr_to_str(curr_a))
    entry_d = add_row("Delay (z^-k):", str(sm.system_delay))
    
    lbl = tk.Label(dialog, text="Delay > 0 adds poles at origin (z^-1)\nDelay < 0 adds zeros at origin (z)", 
                   fg="gray", font=("Arial", 9), pady=10)
    lbl.pack()

    def on_submit():
        try:
            b_str = entry_b.get()
            a_str = entry_a.get()
            
            # Use utility parser
            new_zeros_raw = fmt.parse_complex_list(b_str)
            new_poles_raw = fmt.parse_complex_list(a_str)
            
            delay = int(entry_d.get())
            
            # Calculate Roots
            if len(new_zeros_raw) > 0:
                new_zeros = np.roots(new_zeros_raw).tolist()
            else:
                new_zeros = []
                
            if len(new_poles_raw) > 0:
                new_poles = np.roots(new_poles_raw).tolist()
            else:
                new_poles = []
            
            # Calculate Gain
            gain_num = new_zeros_raw[0] if len(new_zeros_raw) > 0 else 1.0
            gain_den = new_poles_raw[0] if len(new_poles_raw) > 0 and new_poles_raw[0] != 0 else 1.0
            new_gain = abs(gain_num / gain_den)
            
            # Apply to State Manager
            sm.zeros = [complex(z) for z in new_zeros]
            sm.poles = [complex(p) for p in new_poles]
            sm.system_gain = new_gain
            sm.system_delay = delay
            
            # Reset display options
            sm.zeros_opts = [{'show': False, 'show_polar': False} for _ in sm.zeros]
            sm.poles_opts = [{'show': False, 'show_polar': False} for _ in sm.poles]
            
            # Refresh Plots
            update_callback()
            dialog.destroy()
            
        except ValueError as e:
            try:
                import tkinter as tk
                from tkinter import messagebox
                tk.messagebox.showerror("Error", f"Invalid Input: {e}\nUse comma-separated numbers like '1+2j, 3'.")
            except Exception:
                print(f"Error: Invalid Input: {e}")

    import tkinter as tk
    btn = tk.Button(dialog, text="Apply Config", command=on_submit, bg="#ddffdd", font=("Arial", 10, "bold"))
    btn.pack(pady=10, fill='x', padx=20)