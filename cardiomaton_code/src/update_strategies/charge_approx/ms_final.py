"""
    Copy of the main code form `final.ipynb` by @vitraocularia
"""

import numpy as np
from numba import njit

@njit(fastmath=True)
def smooth_transition(x, x0, eps=0.005):
    """
    Sigmoid-based transition function.
    Returns values smoothly varying from 0 to 1 around x0.
    
    eps controls the "width" of the transition region.
    Smaller eps = sharper transition.
    """
    return 1.0 / (1.0 + np.exp(-(x - x0)/eps))

@njit(fastmath=True)
def sigmoid(t, V_lo, V_hi, t0, k):
    """
    Sigmoid-based time-voltage function for potential curve fitting.
    Used for phase 0 estimation (rapid depolarization).
    """
    return V_lo + (V_hi - V_lo) / (1 + np.exp(-(t - t0)/k))

@njit(fastmath=True)
def pacemaker_AP_full(t,
                      V_rest,   # resting membrane potential
                      V_thresh, # threshold potential between slow depolarization and rapid depolarization (phase 4 and phase 0)
                      V_peak,   # peak potential achieved in rapid depolarization
                      t_peak,   # time after which the peak potential is achieved
                      t_end,    # time of the end of a single action potential
                      t_thresh, # time after which the threshold potential is achieved
                      t0_phase0=None, k_phase0=None, # parameters for sigmoid function
                      eps=0.01, # blending width
                    ) -> float:
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

    # clip doesn't work for floats in numba :<
    if T3 <= 0.0:
        u = 0.0
    else:
        u = t3 / T3
    if u < 0.0:
        u = 0.0
    elif u > 1.0:
        u = 1.0
    # u = np.clip(t3 / max(T3, 1e-12), 0.0, 1.0)

    # Hermite-like cubic: V(0)=V_peak, V(T3)=V_rest, V'(0)=0, V'(T3)=0
    # Standard solution:
    # V3(t3) = V_peak*(2*(t3/T3)^3 - 3*(t3/T3)^2 + 1) + V_rest*(-2*(t3/T3)^3 + 3*(t3/T3)^2)
    V3 = V_peak*(2*u**3 - 3*u**2 + 1) + V_rest*(-2*u**3 + 3*u**2)

    # Smooth blending
    w40 = smooth_transition(t, t_thresh, eps)  # blend 4 → 0 near t_thresh
    w03 = smooth_transition(t, t_peak, eps)    # blend 0 → 3 near t_peak
    V = (1 - w40)*V4 + w40*((1 - w03)*V0 + w03*V3)
    return V
