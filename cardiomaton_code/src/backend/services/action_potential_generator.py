import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.special import expit


class ActionPotentialGenerator:
    def __init__(self):
        self.eps = 0.005

    def generate(self, cell_type: str, params: dict, n_cycles: int = 3):
        dt = 0.001

        if cell_type == "PACEMAKER":
            return self._generate_pacemaker(params, n_cycles, dt)
        elif cell_type == "ATRIAL":
            return self._generate_atrial(params, n_cycles, dt)
        elif cell_type == "PURKINJE":
            return self._generate_purkinje(params, n_cycles, dt)
        return None

    @staticmethod
    def _fast_upstroke(t, V_start, V_end, t01):
        k = max(t01, 1e-4) / 12.0
        t_mid = 0.6 * t01
        return V_start + (V_end - V_start) * expit((t - t_mid) / k)

    @staticmethod
    def _smooth_transition(x, x0, eps=0.005):
        return 1.0 / (1.0 + np.exp(-(x - x0) / eps))

    def _generate_atrial(self, p: dict, n_cycles: int, dt: float):
        V34 = p["V_rest"]
        V01 = p["V_peak"]
        V12 = p["V12"]
        V23 = p["V23"]

        t0 = p["t01"]
        t1 = p["t12"]
        t2 = p["t23"]
        t3 = p["t34"]

        t4 = 0.5

        t01 = t0
        t12 = t01 + t1
        t23 = t12 + t2
        t34 = t23 + t3
        t40 = t34 + t4

        t = np.arange(0, t40, dt)

        t_rest = t40 - t34
        t_shift = t - t_rest

        P0 = self._fast_upstroke(t_shift, V34, V01, t01)

        knots_t = [t01, t12, t23, t34]
        knots_V = [V01, V12, V23, V34]

        spline = PchipInterpolator(knots_t, knots_V)
        P13 = spline(t_shift)

        V_cycle = np.where(t < t_rest, V34,
                           np.where(t_shift < t01, P0, P13))

        return self._repeat_cycles(t, V_cycle, t40, n_cycles)

    def _generate_purkinje(self, p: dict, n_cycles: int, dt: float):
        V34 = p["V_rest"]
        V40 = p["V40"]
        V01 = p["V_peak"]
        V12 = p["V12"]
        V23 = p["V23"]

        t01 = p["t01"]
        t12 = t01 + p["t12"]
        t23 = t12 + p["t23"]
        t34 = t23 + p["t34"]
        t40 = t34 + p["t40"]

        t = np.arange(0, t40, dt)

        eps = self.eps

        if V34 >= V40:
            V40 = V34 + 1.0

        t_rest = t40 - t34
        t_shift = t - t_rest

        P4 = V34 + (V40 - V34) * np.clip(t / t_rest, 0, 1)

        P0 = self._fast_upstroke(t_shift, V40, V01, t01)

        knots_t = [t01, t12, t23, t34]
        knots_V = [V01, V12, V23, V34]
        spline = PchipInterpolator(knots_t, knots_V)
        P13 = spline(t_shift)

        w40 = self._smooth_transition(t, t40, eps)
        P40 = (1 - w40) * P4 + w40 * P0

        V = np.where(t_shift < t01, P40, P13)

        return self._repeat_cycles(t, V, t40, n_cycles)

    def _generate_pacemaker(self, p: dict, n_cycles: int, dt: float):
        V34 = p["V_rest"]
        V40 = p["V_thresh"]
        V03 = p["V_peak"]

        t4 = p["t40"]
        t0 = p["t03"]
        t3 = p["t34"]

        t40 = t4
        t03 = t4 + t0
        t34 = t4 + t0 + t3

        t = np.arange(0, t34, dt)

        eps = 0.01

        def sigmoid(t, V_lo, V_hi, t0, k):
            arg = -(t - t0) / k
            arg = np.clip(arg, -700, 700)
            return V_lo + (V_hi - V_lo) / (1 + np.exp(arg))

        def smooth_transition(x, x0, eps):
            arg = -(x - x0)/eps
            arg = np.clip(arg, -700, 700)
            return 1.0 / (1.0 + np.exp(arg))

        t0_phase0 = 0.5 * (t40 + t03)
        k_phase0 = (t03 - t40) / 6.0

        if abs(k_phase0) < 1e-9: k_phase0 = 1e-9

        P0 = sigmoid(t, V40, V03, t0_phase0, k_phase0)

        t_loc = t - t03
        T3 = t34 - t03

        u = np.clip(t_loc / max(T3, 1e-12), 0.0, 1.0)
        P3 = V03 * (2 * u ** 3 - 3 * u ** 2 + 1) + V34 * (-2 * u ** 3 + 3 * u ** 2)

        slope4 = (V40 - V34) / t40
        P4 = V34 + slope4 * t

        w40 = smooth_transition(t, t40, eps)
        w03 = smooth_transition(t, t03, eps)
        V_cycle = (1 - w40) * P4 + w40 * ((1 - w03) * P0 + w03 * P3)

        return self._repeat_cycles(t, V_cycle, t34, n_cycles)

    @staticmethod
    def _repeat_cycles(t_cycle, V_cycle, cycle_duration, n_cycles):
        t_total = []
        V_total = []
        for i in range(n_cycles):
            t_total.append(t_cycle + i * cycle_duration)
            V_total.append(V_cycle)
        return np.concatenate(t_total), np.concatenate(V_total)