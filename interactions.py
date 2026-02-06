# This module manages all user interactions: mouse clicks, drags, 
# context menus, and mode switching. It connects the Matplotlib events 
# to the State Manager and triggers the main update loop.

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

import tkinter as tk
from tkinter import simpledialog, Menu
import numpy as np
import state_manager as sm
import dsp_engine as dsp

# ------------------------------------------------------------
# Module Globals (Injected by Main)
# ------------------------------------------------------------
_tk_root = None
_update_callback = None

def init_interactions(root, callback):
    """
    Initializes the interaction module with the main Tkinter root 
    and the update_all callback function from main.py.
    """
    global _tk_root, _update_callback
    _tk_root = root
    _update_callback = callback

def trigger_update():
    """Safe wrapper to call the main update loop."""
    if _update_callback:
        _update_callback()

# ------------------------------------------------------------
# Mode Control
# ------------------------------------------------------------

def set_mode(m):
    sm.mode = m
    # Optional: Print to console for debug
    # print(f"Mode set to: {sm.mode}")

def set_mode_zero(event): set_mode("zero")
def set_mode_pole(event): set_mode("pole")

# ------------------------------------------------------------
# Z-Plane Interactions (Click, Drag, Context Menu)
# ------------------------------------------------------------

def on_press(event):
    # Verify we are on the Z-plane axis (stored in sm by main)
    if event.inaxes != sm.ax_z: return

    z = event.xdata + 1j * event.ydata
    
    def find_closest(points, threshold=0.2):
        for i, val in enumerate(points):
            if abs(z - val) < threshold: return i
        return None

    z_idx = find_closest(sm.zeros)
    p_idx = find_closest(sm.poles)

    target = None
    if z_idx is not None: target = ("zero", z_idx)
    elif p_idx is not None: target = ("pole", p_idx)

    # Right Click -> Context Menu
    if event.button == 3: 
        if target:
            sm.selected = target
            show_context_menu(event)
        return

    # Double Click -> Edit Coordinate Dialog
    if event.button == 1 and event.dblclick:
        if target:
            sm.selected = target
            set_coordinate()
        return

    # Left Click -> Select/Drag or Add Point
    if event.button == 1:
        if target:
            sm.selected = target
            sm.dragging = target
        else:
            # Adding new points
            if sm.mode == "zero":
                sm.zeros.append(z)
                sm.zeros_opts.append({'show': False, 'show_polar': False})
                
                if sm.add_conjugates and abs(z.imag) > 0.05: 
                    sm.zeros.append(z.conjugate())
                    sm.zeros_opts.append({'show': False, 'show_polar': False})
                trigger_update()
                
            elif sm.mode == "pole":
                sm.poles.append(z)
                sm.poles_opts.append({'show': False, 'show_polar': False})
                
                if sm.add_conjugates and abs(z.imag) > 0.05: 
                    sm.poles.append(z.conjugate())
                    sm.poles_opts.append({'show': False, 'show_polar': False})
                trigger_update()


def on_motion(event):
    if sm.dragging is None or event.inaxes != sm.ax_z: return

    # 1. Get new position
    z_new = event.xdata + 1j * event.ydata
    kind, idx = sm.dragging

    # 2. Get list of points (zeros or poles)
    points = sm.zeros if kind == "zero" else sm.poles

    # 3. Handle "Real Filter" Logic (Conjugate Symmetry)
    if sm.add_conjugates:
        # Get the OLD position before we update it
        z_old = points[idx]

        # Update the dragged point first
        points[idx] = z_new

        # Look for the conjugate pair
        target_conj = z_old.conjugate()
        
        # Find index of the conjugate pair
        pair_idx = None
        min_dist = 0.2 # Threshold
        
        for i, p in enumerate(points):
            if i == idx: continue # Don't match self
            if abs(p - target_conj) < min_dist:
                pair_idx = i
                break
        
        # If a pair exists, update it to be the NEW conjugate
        if pair_idx is not None:
            points[pair_idx] = z_new.conjugate()

    else:
        # Standard Drag (Single point)
        points[idx] = z_new

    trigger_update()

def on_release(event):
    sm.dragging = None

# ------------------------------------------------------------
# Context Menu Logic
# ------------------------------------------------------------

def show_context_menu(event):
    if not _tk_root: return
    
    menu = Menu(_tk_root, tearoff=0)
    menu.add_command(label="Set Coordinate", command=set_coordinate)
    
    kind, idx = sm.selected
    opts = sm.zeros_opts if kind == "zero" else sm.poles_opts
    
    # 1. Cartesian Toggle
    coord_state = opts[idx]['show']
    coord_label = "Hide Rectangular (x,y)" if coord_state else "Show Rectangular (x,y)"
    menu.add_command(label=coord_label, command=toggle_coordinate)

    # 2. Polar Toggle
    polar_state = opts[idx].get('show_polar', False)
    polar_label = "Hide Polar (r,θ)" if polar_state else "Show Polar (r,θ)"
    menu.add_command(label=polar_label, command=toggle_polar)

    menu.add_separator()
    menu.add_command(label="Remove", command=remove_selected)
    
    try:
        # Get coordinates from the GUI event attached to the MPL event
        menu.tk_popup(event.guiEvent.x_root, event.guiEvent.y_root)
    finally:
        menu.grab_release()

def toggle_coordinate():
    if sm.selected is None: return
    kind, idx = sm.selected
    if kind == "zero":
        sm.zeros_opts[idx]['show'] = not sm.zeros_opts[idx]['show']
    else:
        sm.poles_opts[idx]['show'] = not sm.poles_opts[idx]['show']
    trigger_update()

def toggle_polar():
    if sm.selected is None: return
    kind, idx = sm.selected
    if kind == "zero":
        sm.zeros_opts[idx]['show_polar'] = not sm.zeros_opts[idx]['show_polar']
    else:
        sm.poles_opts[idx]['show_polar'] = not sm.poles_opts[idx]['show_polar']
    trigger_update()

def set_coordinate():
    if sm.selected is None or not _tk_root: return

    kind, idx = sm.selected
    current_val = sm.zeros[idx] if kind == "zero" else sm.poles[idx]

    re = simpledialog.askfloat("Set Coordinate", "Real part:", 
                               initialvalue=current_val.real, parent=_tk_root)
    if re is None: return
    
    im = simpledialog.askfloat("Set Coordinate", "Imaginary part:", 
                               initialvalue=current_val.imag, parent=_tk_root)
    if im is None: return

    z_new = re + 1j * im
    if kind == "zero": sm.zeros[idx] = z_new
    else: sm.poles[idx] = z_new

    trigger_update()

def remove_selected():
    if sm.selected is None: return
    kind, idx = sm.selected
    if kind == "zero": 
        sm.zeros.pop(idx)
        sm.zeros_opts.pop(idx)
    else: 
        sm.poles.pop(idx)
        sm.poles_opts.pop(idx)
    sm.selected = None
    trigger_update()

# ------------------------------------------------------------
# Frequency Response Analysis (Click to Measure)
# ------------------------------------------------------------

def on_response_click(event):
    # Verify axes (stored in sm by main)
    if event.inaxes not in [sm.ax_mag, sm.ax_phase]:
        return

    # Setup Colors and Data
    if event.inaxes == sm.ax_mag:
        color = 'navy'
        y_data = np.abs(dsp.compute_H(sm.w_hires))
    else:
        color = 'crimson'
        y_data = np.angle(dsp.compute_H(sm.w_hires))

    # Find closest point on curve (Snap)
    idx = (np.abs(sm.w_hires - event.xdata)).argmin()
    w_snap = sm.w_hires[idx]
    y_snap = y_data[idx]

    # Check for "Tap to Remove" (Clicking existing annotation)
    threshold = 0.15 # Radians tolerance
    
    for i, item in enumerate(sm.response_annotations):
        if item['ax'] == event.inaxes:
            if abs(item['w'] - w_snap) < threshold:
                item['dot'].remove()
                item['txt'].remove()
                sm.response_annotations.pop(i)
                sm.fig.canvas.draw_idle()
                return 

    # Add New Annotation
    dot, = event.inaxes.plot(w_snap, y_snap, 'o', color=color, markersize=6, zorder=10)
    
    text_str = f"({w_snap:.2f} rad, {y_snap:.2f})"
    
    txt = event.inaxes.annotate(
        text_str, 
        xy=(w_snap, y_snap), 
        xytext=(0, 15), textcoords='offset points',
        ha='center', va='bottom',
        fontsize=9, fontweight='bold', 
        color=color,
        bbox=dict(boxstyle="round,pad=0.3", fc="#f0f0f0", ec=color, alpha=0.9),
        arrowprops=dict(arrowstyle='->', color=color),
        zorder=10
    )
    
    sm.response_annotations.append({
        'ax': event.inaxes,
        'w': w_snap,
        'dot': dot,
        'txt': txt
    })
    
    sm.fig.canvas.draw_idle()