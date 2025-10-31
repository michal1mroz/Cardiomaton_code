import json
from math import cos, sin, pi
import numpy as np
from scipy.interpolate import CubicSpline

def load_approx_from_coefficients(path : str = "./resources/func_coeffs/", filename : str = "aprox_coeffs.json"):
    file = path + filename
    with open(file, 'r') as f:
        data = json.load(f)
    a = data["a"]
    b = data["b"]
    a_s = data["a_s"]
    b_s = data["b_s"]
    m = data["m"]
    print(a_s)
    print(b_s)


    def trn(x):
        return 2 * pi * ((x - a) / (b - a)) - pi
    def f(x):
        x = trn(x)
        return  a_s[0]/2 + sum(a_s[k] * cos(k * x) + b_s[k] * sin(k * x) for k in range(1, m+1))
    return f

def load_spline_from_coefficients(path : str = "./resources/func_coeffs/", filename : str = "spline_coeffs.json"):
    file = path + filename
    with open(file, 'r') as f:
        data = json.load(f)
    x = np.array(data["x"])
    c = np.array(data["c"])

    cs = CubicSpline(x, np.zeros_like(x), bc_type='periodic')
    cs.c = c
    return cs