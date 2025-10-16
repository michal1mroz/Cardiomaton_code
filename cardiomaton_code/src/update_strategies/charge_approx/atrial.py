import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.special import expit


def fast_upstroke(t, V_start, V_end, t01):
    """Steep sigmoid upstroke, numerically stable"""
    k = max(t01, 1e-4) / 12.0
    t_mid = 0.6 * t01
    return V_start + (V_end - V_start) * expit((t - t_mid)/k)

def atrial_AP(t,
              V34=-85.0,
              V01=+20.0,
              V12=+5.0,
              V23=-15.0,
              t01=0.004,
              t12=0.015,
              t23=0.070,
              t34=0.170,
              t40=2.0):

    # Phase 4 duration
    t_rest = t40 - t34
    t_shift = t - t_rest

    # Phase 0
    P0 = fast_upstroke(t_shift, V34, V01, t01)

    # Phases 1-3
    knots_t = [t01, t12, t23, t34]
    knots_V = [V01, V12, V23, V34]
    spline = PchipInterpolator(knots_t, knots_V)
    P13 = spline(t_shift)

    # Total potential
    V = np.where(t < t_rest, V34,
                 np.where(t_shift < t01, P0, P13))
    return V