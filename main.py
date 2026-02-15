# This is the main entry point for the PoZeDSP tool.
# It initializes the GUI layout, sets up the Matplotlib figure/axes,
# defines the high-level callbacks (Reset, Update, Menu), and starts the event loop.

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

import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons, TextBox
import tkinter as tk
from tkinter import Menu
import numpy as np

# Local Modules
import state_manager as sm
import dsp_engine as dsp
import ui_components as ui
import interactions as interact
import formatting_utils as fmt

# ------------------------------------------------------------
# 1. Setup & Styling
# ------------------------------------------------------------
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 16,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.labelweight': 'bold'
}) 

# Initialize hidden Tk root for dialogs
root = tk.Tk()
root.withdraw()

# ------------------------------------------------------------
# 2. Figure & Axes Layout
# ------------------------------------------------------------
fig = plt.figure(figsize=(16, 10))
sm.fig = fig # Store in state manager for other modules

# Main Plots
ax_z = fig.add_axes([0.01, 0.32, 0.38, 0.58])
ax_mag = fig.add_axes([0.38, 0.6, 0.45, 0.25])
ax_phase = fig.add_axes([0.38, 0.32, 0.45, 0.20])
ax_imp = fig.add_axes([0.05, 0.05, 0.90, 0.20])

# Store axes in State Manager so interactions.py can access them
sm.ax_z = ax_z
sm.ax_mag = ax_mag
sm.ax_phase = ax_phase

# Titles & Labels
ax_z.set_title("Z-plane", fontweight='bold', fontsize=15)
ax_z.set_xlabel("Real-Part", fontweight='bold', fontsize=14)
ax_z.set_ylabel("Imaginary-Part", fontweight='bold', fontsize=14)
ax_z.set_aspect("equal")
ax_z.grid(True, linestyle=':', alpha=0.6)

# Initial empty plots
theta = np.linspace(0, 2*np.pi, 400)
ax_z.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.6)
zero_plot, = ax_z.plot([], [], 'o', color='blue', markeredgewidth=2, markerfacecolor='none', markersize=12, label='Zeros')
pole_plot, = ax_z.plot([], [], 'x', color='red', markeredgewidth=3, markersize=12, label='Poles')
ax_z.legend(loc='lower right', fontsize=12)

mag_line, = ax_mag.plot([], [], color="navy", linewidth=2.5)
ax_mag.set_title("Magnitude Response", fontweight='bold', fontsize=15)
ax_mag.set_xlim(-np.pi, np.pi)
ax_mag.grid(False)

phase_line, = ax_phase.plot([], [], color="crimson", linewidth=2.5)
ax_phase.set_title("Phase Response", fontweight='bold', fontsize=15)
ax_phase.set_xlim(-np.pi, np.pi)
ax_phase.set_ylim(-np.pi, np.pi)
ax_phase.grid(False)

ax_imp.set_ylabel("Impulse Response", fontweight='bold', fontsize=14)
ax_imp.grid(True, linestyle=':', alpha=0.6)

# Transfer Function Text Object
tf_text = fig.text(
    0.6, 0.95, "", fontsize=18, ha="center", va="center",
    bbox=dict(boxstyle="round,pad=0.5", fc="#f9f9f9", ec="#333", alpha=1.0, linewidth=1.5),
    picker=True
)
sm.tf_text_artist = tf_text # Store for click detection

# ------------------------------------------------------------
# 3. Sidebar UI Controls
# ------------------------------------------------------------
panel_x = 0.85

# A. Reset Button
ax_reset = fig.add_axes([0.85, 0.70, 0.12, 0.05])
btn_reset = Button(ax_reset, "Reset", color='#ffdddd', hovercolor='#ffaaaa')
btn_reset.label.set_fontsize(16)        
btn_reset.label.set_fontweight('bold')   

# B. Signal Analysis Controls
# Labels
ax_lbl = fig.add_axes([panel_x, 0.60, 0.12, 0.03])
ax_lbl.axis('off')
ax_lbl.text(0.4, 0, "x[n]", fontweight='bold', fontsize=15)
ax_txt = fig.add_axes([panel_x, 0.55, 0.12, 0.04])

ax_lbl_n = fig.add_axes([0.85, 0.65, 0.03, 0.03]) 
ax_lbl_n.axis('off')
ax_lbl_n.text(0, 0.5, "Sample Length:", fontweight='bold', va='center', fontsize=13)

# Text Boxes
ax_txt_n = fig.add_axes([0.925, 0.65, 0.045, 0.032])
txt_n = TextBox(ax_txt_n, "", initial="200")
txt_n.label.set_fontsize(9)

txt_sig = TextBox(ax_txt, "", initial="")
txt_sig.text_disp.set_horizontalalignment('left')
txt_sig.text_disp.set_clip_on(True)
txt_sig.ax.set_xlim(0, 1)

# Apply custom textbox logic
ui.setup_advanced_textbox(txt_sig, root)

# Store textboxes in state manager for ui_components to access
sm.txt_n = txt_n
sm.txt_sig = txt_sig

# Simulate Button
ax_sim = fig.add_axes([panel_x, 0.46, 0.12, 0.05])
btn_sim = Button(ax_sim, "Simulate", color='#ddffdd', hovercolor='#bbffbb')
btn_sim.label.set_fontweight('bold')
btn_sim.on_clicked(ui.show_signal_analysis)

# C. Real Filter Checkbox
ax_check = fig.add_axes([0.85, 0.39, 0.14, 0.05], frameon=False)
check = CheckButtons(ax_check, ['Real Filter'], [False])
for lbl in check.labels:
    lbl.set_fontsize(14)
    lbl.set_fontweight('bold')
    lbl.set_fontfamily('sans-serif')

# Find the rectangle to change color later
check_box_rect = None
for artist in ax_check.patches:
    if isinstance(artist, matplotlib.patches.Rectangle):
        check_box_rect = artist
        check_box_rect.set_facecolor('white')
        check_box_rect.set_edgecolor('black')
        break

# D. FFT Dropdown
ax_fft_btn = fig.add_axes([0.85, 0.32, 0.12, 0.05])
btn_fft = Button(ax_fft_btn, f"FFT Points: {sm.N_impulse}", color='#ddffff', hovercolor='#aaffff')
btn_fft.label.set_fontsize(14)
btn_fft.label.set_fontweight('bold')

# E. Zero/Pole Buttons (Top Left)
btn_width = 0.06; btn_height = 0.06; btn_gap = 0.01; start_x = 0.05; start_y = 0.90
ax_zero_btn = plt.axes([start_x, start_y, btn_width, btn_height])
ax_pole_btn = plt.axes([start_x + btn_width + btn_gap, start_y, btn_width, btn_height])

btn_zero = Button(ax_zero_btn, "", hovercolor='0.9')
btn_pole = Button(ax_pole_btn, "", hovercolor='0.9')
ui.decorate_button(ax_zero_btn, 'zero')
ui.decorate_button(ax_pole_btn, 'pole')

btn_zero.on_clicked(interact.set_mode_zero)
btn_pole.on_clicked(interact.set_mode_pole)

# ------------------------------------------------------------
# 4. Core Update Logic
# ------------------------------------------------------------

def update_all():
    """
    The main render loop. Refreshes all plots, text, and overlays 
    based on the current state in state_manager.
    """
    
    # 1. Clear Annotation Artifacts
    for item in sm.response_annotations:
        try:
            item['dot'].remove()
            item['txt'].remove()
        except ValueError: pass
    sm.response_annotations = []
    
    # 2. Update Z-Plane Points
    zero_plot.set_data([z.real for z in sm.zeros], [z.imag for z in sm.zeros])
    pole_plot.set_data([p.real for p in sm.poles], [p.imag for p in sm.poles])

    # 3. Dynamic Z-Plane Scaling
    all_points = sm.zeros + sm.poles
    max_mag = max([abs(p) for p in all_points]) if all_points else 0
    limit = max(1.2, max_mag * 1.2)
    ax_z.set_xlim(-limit, limit)
    ax_z.set_ylim(-limit, limit)

    H = dsp.compute_H(sm.w_hires)
    mag_linear = np.abs(H)
    
    max_val = np.max(mag_linear)
    if max_val > 1e-9:
        mag_norm = mag_linear / max_val
    else:
        mag_norm = mag_linear
        
    mag_db = 20 * np.log10(mag_norm + 1e-12)

    mag_line.set_data(sm.w_hires, mag_db)
    phase_line.set_data(sm.w_hires, np.angle(H))
    
    min_db = np.min(mag_db)
    bottom_limit = -60 
    if bottom_limit > -10: 
        bottom_limit = -10
        
    ax_mag.set_ylim(bottom=bottom_limit, top=5) 
    ax_mag.set_xlim(-np.pi, np.pi)
  
    b, a = dsp.coeffs_quantized()
    
    delay_str = ""
    if sm.system_delay != 0:
        if sm.system_delay == 1: delay_str = "z^{-1} \\cdot"
        elif sm.system_delay == -1: delay_str = "z \\cdot "
        else: delay_str = f"z^{{{-sm.system_delay}}} \\cdot "
            
    tf_str = rf"$\mathbf{{H(z)}} = {delay_str}\frac{{{fmt.poly_to_mathtext(b)}}}{{{fmt.poly_to_mathtext(a)}}}$"
    tf_text.set_text(tf_str)

    # 6. Update Impulse Response
    ax_imp.cla()
    ax_imp.set_ylabel("Impulse Response", fontweight='bold', fontsize=14)
    ax_imp.grid(True, linestyle=':', alpha=0.6)
    
    n, h = dsp.stable_impulse_response()
    ax_imp.stem(n, h, basefmt=" ", linefmt='C0-', markerfmt='C0o')

    # 7. Draw Overlays (Coordinates)
    # Clear old text
    for txt in ax_z.texts:
        txt.remove()
        
    def draw_overlays(points, opts, color):
        for i, p in enumerate(points):
            if i >= len(opts): continue
            y_offset = 0.15
            
            # Cartesian
            if opts[i]['show']:
                text_str = f"({p.real:.2f}, {p.imag:.2f})"
                ax_z.text(p.real, p.imag + y_offset, text_str,
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color=color,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, alpha=0.9))
                y_offset += 0.15

            # Polar
            if opts[i].get('show_polar', False):
                r = abs(p); theta = np.angle(p)
                text_str = f"({r:.2f}, {theta:.2f} rad)"
                ax_z.text(p.real, p.imag + y_offset, text_str,
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='black',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#f0f0f0", ec="black", alpha=0.9))

    draw_overlays(sm.zeros, sm.zeros_opts, 'blue')
    draw_overlays(sm.poles, sm.poles_opts, 'red')

    # 8. Draw Delay Visuals (Origin Points)
    for artist in sm.delay_artists: 
        try: artist.remove()
        except ValueError: pass
    sm.delay_artists = []
    
    if sm.system_delay != 0:
        marker = 'x' if sm.system_delay > 0 else 'o'
        color = '#000000'
        marker_color = 'none' if sm.system_delay > 0 else color
        
        pt, = ax_z.plot(0, 0, marker=marker, color=color, 
                        markeredgecolor=color, markerfacecolor=marker_color,
                        markersize=14, markeredgewidth=2, alpha=0.5, zorder=1)
        sm.delay_artists.append(pt)
        
        count = abs(sm.system_delay)
        if count > 1:
            txt = ax_z.text(0.1, 0, f"{count}", color='gray', fontsize=14, fontweight='bold')
            sm.delay_artists.append(txt)

    # 9. Refresh Popup if open
    if sm.signal_fig is not None and plt.fignum_exists(sm.signal_fig.number):
        ui.show_signal_analysis()

    fig.canvas.draw_idle()

# ------------------------------------------------------------
# 5. Callback Implementations
# ------------------------------------------------------------

def reset_board(event):
    # Clear visual lists
    for artist in sm.vector_artists:
        try: artist.remove()
        except: pass
    sm.vector_artists = []
    
    for item in sm.response_annotations: 
        try: item['dot'].remove(); item['txt'].remove()
        except: pass
    sm.response_annotations = []

    for artist in sm.delay_artists: 
        try: artist.remove()
        except: pass
    sm.delay_artists = []

    if sm.ghost_artist:
        try: sm.ghost_artist.remove()
        except: pass
        sm.ghost_artist = None
    
    sm.mode = None
    
    # Reset State
    sm.zeros = []
    sm.poles = []
    sm.zeros_opts = []
    sm.poles_opts = []
    sm.selected = None
    sm.system_gain = 1.0
    sm.system_delay = 0
    
    # Reset UI
    sm.txt_sig.set_val("")
    sm.txt_n.set_val("200")
    if sm.signal_fig:
        try:
            plt.close(sm.signal_fig) # Properly close the window
        except: pass
        sm.signal_fig = None
    
    update_all()
    fig.canvas.draw()
    fig.canvas.flush_events()

def toggle_conjugates(label):
    sm.add_conjugates = not sm.add_conjugates
    
    # Update UI Color
    if check_box_rect:
        if sm.add_conjugates:
            check_box_rect.set_facecolor('#40E0D0') # Turquoise/Blue active
        else:
            check_box_rect.set_facecolor('white')   # White inactive
    fig.canvas.draw()
    fig.canvas.flush_events()

def show_fft_menu(event):
    fft_menu = Menu(root, tearoff=0)
    options = [64, 128, 256, 512, 1024, 2048]
    
    def set_fft(val):
        sm.N_impulse = val
        btn_fft.label.set_text(f"FFT Points: {val}")
        update_all()

    for opt in options:
        fft_menu.add_command(label=str(opt), command=lambda v=opt: set_fft(v))
    
    try:
        x_root = root.winfo_pointerx()
        y_root = root.winfo_pointery()
        fft_menu.tk_popup(x_root, y_root)
    finally:
        fft_menu.grab_release()

# ------------------------------------------------------------
# 6. Connections & Start
# ------------------------------------------------------------

# Connect UI Callbacks
btn_reset.on_clicked(reset_board)
check.on_clicked(toggle_conjugates)
btn_fft.on_clicked(show_fft_menu)

# Initialize Interaction Module
interact.init_interactions(root, update_all)

# Connect Matplotlib Events to Interaction Module
fig.canvas.mpl_connect("button_press_event", interact.on_press)
fig.canvas.mpl_connect("motion_notify_event", interact.on_motion)
fig.canvas.mpl_connect("button_release_event", interact.on_release)
fig.canvas.mpl_connect("button_press_event", interact.on_response_click)
fig.canvas.mpl_connect('key_press_event', interact.on_key_press)

# Special Case: Transfer Function Editor needs root and callback passed
fig.canvas.mpl_connect('pick_event', lambda e: ui.open_tf_editor(e, root, update_all))

# Initial Draw
update_all()
plt.show()