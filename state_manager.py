# This file serves as the central state container for the PoZeDSP tool.
# It holds global variables for filter coefficients (poles/zeros), UI interaction 
# states, and plotting references to prevent circular imports between modules.

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

import numpy as np

# ------------------------------------------------------------
# Global State Variables
# ------------------------------------------------------------

# Mathematical State (Filter Design)
zeros = []
poles = []
system_gain = 1.0
system_delay = 0

# UI & Interaction State
mode = None         # Current tool mode: 'zero' or 'pole'
dragging = None     # Currently dragged element
selected = None     # Currently selected element (for context menu)
add_conjugates = False # Toggle for real-filter mode
ghost_artist = None    # Stores the temporary visual for drag-and-drop
current_theme = 'dark' # 'dark' or 'light'

# Plotting & Visualization Storage
zeros_opts = []     # Display options for zeros (polar/cartesian visibility)
poles_opts = []     # Display options for poles
vector_artists = [] # Lines connecting poles/zeros (if implemented)
response_annotations = [] # Markers on magnitude/phase plots
delay_artists = []  # Visual indicators for system delay (origin poles/zeros)
signal_fig = None   # Reference to the independent signal analysis window

# Frequency Vectors
w_hires = np.linspace(-np.pi, np.pi, 2048) # High-res axis for smooth plotting
N_impulse = 64      # Number of points for FFT/Impulse calculation