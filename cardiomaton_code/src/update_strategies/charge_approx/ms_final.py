"""
    Copy of the main code form `final.ipynb` by @vitraocularia
"""

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, IntSlider

def smooth_transition(x, x0, eps=0.005):
    """
    Sigmoid-based transition function.
    Returns values smoothly varying from 0 to 1 around x0.
    
    eps controls the "width" of the transition region.
    Smaller eps = sharper transition.
    """
    return 1.0 / (1.0 + np.exp(-(x - x0)/eps))

def sigmoid(t, V_lo, V_hi, t0, k):
    """
    Sigmoid-based time-voltage function for potential curve fitting.
    Used for phase 0 estimation (rapid depolarization).
    """
    return V_lo + (V_hi - V_lo) / (1 + np.exp(-(t - t0)/k))

def pacemaker_AP_full(t,
                      V_rest,   # resting membrane potential
                      V_thresh, # threshold potential between slow depolarization and rapid depolarization (phase 4 and phase 0)
                      V_peak,   # peak potential achieved in rapid depolarization
                      t_peak,   # time after which the peak potential is achieved
                      t_end,    # time of the end of a single action potential
                      t_thresh, # time after which the threshold potential is achieved
                      t0_phase0=None, k_phase0=None, # parameters for sigmoid function
                      eps=0.01): # blending width
    """
    Phase 4: linear
    Phase 0: sigmoid
    Phase 3: cubic (zero slope at peak and end)
    Smoothly blended at t_thresh and t_peak.
    """
    if t0_phase0 is None:
        t0_phase0 = 0.5*(t_thresh + t_peak)
    if k_phase0 is None:
        k_phase0 = (t_peak - t_thresh)/6.0

    # Phase 0 - rapid depolarization
    V0 = sigmoid(t, V_thresh, V_peak, t0_phase0, k_phase0)

    # Phase 4 - slow depolarization
    slope4 = (V_thresh - V_rest) / t_thresh
    V4 = V_rest + slope4 * t

    # Phase 3 - repolarization
    t3 = t - t_peak
    T3 = t_end - t_peak
    # Hermite-like cubic: V(0)=V_peak, V(T3)=V_rest, V'(0)=0, V'(T3)=0
    # Standard solution:
    # V3(t3) = V_peak*(2*(t3/T3)^3 - 3*(t3/T3)^2 + 1) + V_rest*(-2*(t3/T3)^3 + 3*(t3/T3)^2)
    u = np.clip(t3 / max(T3, 1e-12), 0.0, 1.0)
    V3 = V_peak*(2*u**3 - 3*u**2 + 1) + V_rest*(-2*u**3 + 3*u**2)

    # Smooth blending
    w40 = smooth_transition(t, t_thresh, eps)  # blend 4 → 0 near t_thresh
    w03 = smooth_transition(t, t_peak, eps)    # blend 0 → 3 near t_peak
    V = (1 - w40)*V4 + w40*((1 - w03)*V0 + w03*V3)
    return V


def interactive_pacemaker(V_rest=-60.0, V_thresh=-40.0, V_peak=15.0,
                          t_thresh=0.35, t_peak=0.45, t_end=0.80,
                          n_cycles=2, eps=0.005):
    # Time axis
    t_cycle = np.linspace(0, t_end, 600)
    V_cycle = pacemaker_AP_full(t_cycle,
                                V_rest, V_thresh, V_peak,
                                t_peak, t_end, t_thresh, 
                                t0_phase0=None, k_phase0=None,
                                eps=eps)
    # Repeat cycles
    t_total = np.linspace(0, n_cycles*t_end, n_cycles*len(t_cycle))
    V_total = np.tile(V_cycle, n_cycles)

    # Plot
    plt.figure(figsize=(9,4))
    plt.plot(t_total, V_total, lw=2)
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (mV)")
    plt.title("Interactive Pacemaker AP model")
    plt.grid(True)
    plt.ylim(V_rest-10, V_peak+10)
    plt.show()

# Create sliders
if __name__ == '__main__':
    interact(interactive_pacemaker,
         V_rest=FloatSlider(value=-60, min=-80, max=-50, step=1, description="Maximum Diastolic Potential (mV)"),
         V_thresh=FloatSlider(value=-40, min=-60, max=-20, step=1, description="Threshold Potential (mV)"),
         V_peak=FloatSlider(value=15, min=0, max=40, step=1, description="Peak Membrane Potential (mV)"),
         t_thresh=FloatSlider(value=0.35, min=0.2, max=0.5, step=0.05, description="Slow Depolarization Duration (s)"),
         t_peak=FloatSlider(value=0.45, min=0.3, max=0.7, step=0.05, description="Rapid Depolarization Duration (s)"),
         t_end=FloatSlider(value=0.80, min=0.5, max=1.2, step=0.05, description="Repolarization Duration (s)"),
         n_cycles=IntSlider(value=2, min=1, max=5, step=1, description="Cycles"),
         eps=FloatSlider(value=0.005, min=0.005, max=0.02, step=0.005, description="Blend width")
        )
