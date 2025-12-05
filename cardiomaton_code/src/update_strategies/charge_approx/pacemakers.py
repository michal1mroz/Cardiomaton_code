import numpy as np
from scipy.special import expit

def smooth_transition(x, x0, eps=0.005):
    """
    Sigmoid-based transition function.
    Returns values smoothly varying from 0 to 1 around x0.
    
    eps controls the "width" of the transition region.
    Smaller eps = sharper transition.
    """
    return expit((x - x0) / eps)

def sigmoid(t, V_lo, V_hi, t0, k):
    """
    Sigmoid-based time-voltage function for potential curve fitting.
    Used for phase 0 estimation (rapid depolarization).

    can the exp ever explode here??? @mm
    """
    return V_lo + (V_hi - V_lo) * expit((t-t0)/k)
# / (1 + np.exp(-(t - t0)/k))

def pacemaker_AP(t,
                 V_rest, V_thresh, V_peak, 
                 t03, t34, t40,
                 eps=0.01):
    """
    Phase 0: sigmoid
    Phase 3: cubic (zero slope at peak and end)
    Phase 4: linear
    Smoothly blended at t_thresh and t_peak.
    """
    # Phase 0 - rapid depolarization
    t0_phase0 = 0.5*(t40 + t03)
    k_phase0 = (t03 - t40)/6.0
    P0 = sigmoid(t, V_thresh, V_peak, t0_phase0, k_phase0)

    # Phase 3 - repolarization
    t3 = t - t03
    T3 = t34 - t03
    # Hermite-like cubic: V(0)=V03, V(T3)=V34, V'(0)=0, V'(T3)=0
    # Standard solution:
    # V3(t3) = V_peak*(2*(t3/T3)^3 - 3*(t3/T3)^2 + 1) + V_rest*(-2*(t3/T3)^3 + 3*(t3/T3)^2)
    u = np.clip(t3 / max(T3, 1e-12), 0.0, 1.0)
    P3 = V_peak *(2*u**3 - 3*u**2 + 1) + V_rest*(-2*u**3 + 3*u**2)

    # Phase 4 - slow depolarization
    slope4 = (V_thresh - V_rest) / t40
    P4 = V_rest + slope4 * t

    # Smooth blending
    w40 = smooth_transition(t, t40, eps)
    w03 = smooth_transition(t, t03, eps)
    V = (1 - w40)*P4 + w40*((1 - w03)*P0 + w03*P3)
    return V