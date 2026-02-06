# This module contains the core mathematical functions for the PoZeDSP tool.
# It handles signal generation, Z-transform calculations, digital filtering
# (difference equations), and impulse response derivation via FFT.

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
import state_manager as sm

# ------------------------------------------------------------
# Basic Signal Generators
# ------------------------------------------------------------

def unit_step(t):
    """Generates a unit step signal: u[n] = 1 for n >= 0."""
    return np.where(t >= 0, 1.0, 0.0)

def impulse(t):
    """Generates a unit impulse: delta[n] = 1 for n == 0."""
    return np.where(np.abs(t) < 1e-9, 1.0, 0.0)

def ramp(t):
    """Generates a ramp signal: r[n] = n * u[n]."""
    return t * unit_step(t)

def rect(t, width):
    """Generates a rectangular pulse of specified width."""
    return np.where((t >= 0) & (t < width), 1.0, 0.0)

# ------------------------------------------------------------
# Digital Filtering Core
# ------------------------------------------------------------

def filter_signal(b, a, x):
    """
    Implements a Direct Form II structure to filter signal x
    using numerator coeffs b and denominator coeffs a.
    """
    # Normalize by a[0] if necessary
    if a[0] != 1.0 and a[0] != 0:
        b = b / a[0]
        a = a / a[0]
        
    y = np.zeros_like(x)
    M, N = len(b), len(a)
    
    # Standard Difference Equation Implementation
    for n in range(len(x)):
        # Feedforward part (b coefficients)
        for k in range(M):
            if n - k >= 0: y[n] += b[k] * x[n - k]
            
        # Feedback part (a coefficients)
        for m in range(1, N):
            if n - m >= 0: y[n] -= a[m] * y[n - m]
            
    return y

# ------------------------------------------------------------
# Z-Transform & Response Analysis
# ------------------------------------------------------------

def compute_H(w_vals):
    """
    Computes the complex Frequency Response H(e^jw) for the current 
    poles and zeros in the global state.
    """
    z = np.exp(1j * w_vals)
    H = np.ones_like(z, dtype=complex)
    
    # Apply System Gain
    H *= sm.system_gain
    
    # Apply System Delay (z^k or z^-k)
    if sm.system_delay != 0:
        H *= (z ** sm.system_delay)

    # Accumulate Zeros: (1 - z0 * z^-1) -> H *= (1 - z0/z)
    for z0 in sm.zeros:
        H *= (1 - z0 / z)

    # Accumulate Poles: 1 / (1 - p0 * z^-1)
    for p0 in sm.poles:
        denom = (1 - p0 / z)
        # Avoid division by zero singularities
        denom[abs(denom) < 1e-10] = 1e-10 
        H /= denom

    return H

def coeffs_quantized():
    """
    Converts roots (poles/zeros) to polynomial coefficients (b, a)
    and quantizes them to 3 decimal places for display.
    """
    b = np.poly(sm.zeros) if sm.zeros else np.array([1.0])
    a = np.poly(sm.poles) if sm.poles else np.array([1.0])
    
    # Scale numerator by system gain
    b = b * sm.system_gain
    
    return np.round(b, 3), np.round(a, 3) 

def stable_impulse_response():
    """
    Computes the impulse response using the Inverse FFT of the 
    frequency response. This method is stable even for unstable filters
    because it evaluates on the unit circle.
    """
    # Recalculate frequency grid based on current N_impulse
    k = np.arange(sm.N_impulse)
    w_fft = 2 * np.pi * k / sm.N_impulse 
    
    H_fft = compute_H(w_fft)
    
    h = np.fft.ifft(H_fft)
    h_shifted = np.fft.fftshift(h)
    
    n = np.arange(-sm.N_impulse//2, sm.N_impulse//2)
    return n, np.real(h_shifted)