import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.special import expit


def smooth_transition(x, x0, eps=0.005):
    """
    Sigmoid-based transition function.
    Returns values smoothly varying from 0 to 1 around x0.
    
    eps controls the "width" of the transition region.
    Smaller eps = sharper transition.
    """
    return expit((x - x0) / eps)
#1.0 / (1.0 + np.exp(-(x - x0)/eps))

def fast_upstroke(t, V_start, V_end, t01):
    """Steep sigmoid upstroke, numerically stable"""
    k = max(t01, 1e-4) / 12.0
    t_mid = 0.6 * t01
    return V_start + (V_end - V_start) * expit((t - t_mid)/k)

def purkinje_AP(t, 
                V_rest, V40, V_peak, V12, V23,
                t01, t12, t23, t34, t40,
                eps=0.005):
    """
    Returns one full AP cycle including phase 4 slow depolarization.
    """

    if V_rest >= V40:
        V40 = V_rest + 1.0

    t_rest = t40 - t34
    t_shift = t - t_rest

    #  Phase 4
    P4 = V_rest + (V40 - V_rest) * np.clip(t / t_rest, 0, 1)

    # Phase 0
    P0 = fast_upstroke(t_shift, V40, V_peak, t01)

    # Phases 1-3
    knots_t = [t01, t12, t23, t34]
    knots_V = [V_peak, V12, V23, V_rest]
    spline = PchipInterpolator(knots_t, knots_V)
    P13 = spline(t_shift)

    # Smooth transition between phase 4 and phase 0 
    w40 = smooth_transition(t, t40, eps) 
    P40 = (1 - w40) * P4 + w40 * P0 
    
    # Total potential 
    V = np.where(t_shift < t01, P40, P13)
    return V