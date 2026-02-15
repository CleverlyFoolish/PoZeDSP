# PoZeDSP: Pole-Zero Digital Signal Processing Tool

**PoZeDSP** is a software for designing and analyzing digital filters from their pole-zero geometry. It provides engineers and students with an interface to visualize the Z-plane, analyze frequency responses, and simulate filter performance on different signals.

##  Key Features

### 1. Interactive Z-Plane Design
* **Drag-and-Drop Interface:** Place poles and zeros on the complex Z-plane.
* **Real-Time Updates:** Moving a pole or zero instantly updates the Magnitude, Phase, and Impulse response plots.
* **Coordinate Precision:** Double-click any point to set exact Cartesian $(x, y)$ coordinates, or use the context menu to toggle Polar $(r, \theta)$ display.

### 2. Filter Analysis and Designer Tools
* **Real Filter Mode:** Automatically enforces conjugate symmetry. If you add or move a complex pole/zero, its conjugate is automatically created and synchronized, ensuring the filter coefficients remain real-valued.
* **Transfer Function Editor:** View the exact transfer function $H(z)$. Click the equation to manually edit the numerator ($b$) and denominator ($a$) coefficients.
* **Frequency Response:** Visualization of Magnitude and Phase responses.
* **Impulse Response:** Calculates the stable impulse response $h[n]$ using IFFT of Frequency Response.
* **Adjustable Resolution:** Change the FFT size (64 to 2048 points) for better time-domain detail.

### 3. Filtering Simulator
* **Custom Input Signals:** Define inputs using mathematical expressions (e.g., `sin(0.1*n) + 0.5*d(n-5)`).
* **Live Filtering:** Simulates the filter processing the input signal and displays input vs. output overlays in a separate analysis window.
* **Supported Waveforms** Supports standard signals like Unit Step $u[n]$, Impulse $\delta[n]$, Ramp $r[n]$, and Rectangular pulses.

---

##  Installation

### Prerequisites
* Python 3.8 or higher
* `pip` package manager

### Setup
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/CleverlyFoolish/PoZeDSP.git
    cd PoZeDSP
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    python main.py
    ```

---

##  Usage Guide

### The Workspace
The interface is divided into four main sections:
1.  **Z-Plane (Left):** Your main design area.
2.  **Response Graphs (Right):** Magnitude and Phase plots.
3.  **Impulse Response (Bottom):** Time-domain visualization.
4.  **Control Panel** Signal inputs and configuration.

### Controls & Shortcuts

| Action | Mouse/Key | Description |
| :--- | :--- | :--- |
| **Add Point** | **Left Click** | Adds a Pole or Zero (depending on selected mode). |
| **Move Point** | **Drag** | Moves the selected point. |
| **Cancel Mode** | `Esc` | Cancels "Add Pole/Zero" mode without placing anything. |
| **Context Menu** | **Right Click** | Opens menu to Remove point or toggle coordinates. |
| **Edit Value** | **Double Click** | Opens dialog to type exact coordinates. |
| **Measure** | **Click on Graph** | Adds a data tip (tooltip) to the Mag/Phase response. |
| **Pan/Zoom** | **Toolbar** | Use standard Matplotlib toolbar at bottom. |

### Designing a Filter
1.  Select **"Add Zero"** (Blue Circle) or **"Add Pole"** (Red X) from the top-left toolbar.
2.  Click anywhere on the Z-plane to place it.
3.  Enable **"Real Filter"** in the sidebar to ensure complex points always appear in conjugate pairs.
4.  Click the **$H(z)$ Equation** at the top to manually fine-tune coefficients or add system delay ($z^{-k}$).

### Signal Simulation Syntax
In the "x[n]" text box, you can write Python expressions using `n` as the time vector. The tool supports standard `numpy` functions and special DSP shortcuts:

| Function | Syntax | Description |
| :--- | :--- | :--- |
| **Impulse** $\delta[n]$ | `d(n)` or `impulse(n)` | 1 at $n=0$, 0 otherwise. |
| **Unit Step** $u[n]$ | `u(n)` or `step(n)` | 1 for $n \ge 0$, 0 otherwise. |
| **Ramp** $r[n]$ | `r(n)` | $n$ for $n \ge 0$. |
| **Rectangular** | `rect(n, W)` | 1 for $0 \le n < W$. |
| **Sine/Cos** | `sin(w*n)`, `cos(w*n)` | Standard trigonometric functions. |
| **Exponential** | `exp(a*n)` | $e^{a*n}$ |
| **Pulse Train** | `pt(start, space, num)` | Generates `num` impulses starting at `start`, spaced by `space`. <br> *Example:* `pt(0, 10, 5)` |
| **Noise** | `random.randn(len(n))` | Gaussian white noise. |

**Example Signals:**
* `cos(0.2*pi*n) + 0.5*random.randn(len(n))` (Noisy Cosine)
* `u(n) - u(n-10)` (Pulse of width 10)
* `0.9**n * u(n)` (Decaying Exponential)

---

##  Building the Executable
To distribute PoZeDSP as a standalone file (no Python required):

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Run the build command:
    ```bash
    pyinstaller --onefile --windowed --name PoZeDSP_v1.0 main.py
    ```
3.  The executable will appear in the `dist/` folder.

---

##  License
Copyright (C) 2026 Rishabh Shetty

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License** as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the `LICENSE` file for more details.