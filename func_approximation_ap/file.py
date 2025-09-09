import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
import json

# -------------- Data Utils -------------

def load_spline_from_coefficients(filename='spline_coeffs.json'):
    with open(filename, 'r') as f:
        data = json.load(f)
    x = np.array(data["x"])
    c = np.array(data["c"])
    bc_type = data.get("bc_type", 'periodic')

    # Tworzymy pusty CubicSpline i nadpisujemy współczynniki
    cs = CubicSpline(x, np.zeros_like(x), bc_type='periodic')  # y nie ma znaczenia
    cs.c = c
    return cs

def load_aprox_from_coefficients(filename='aprox_coeffs.json'):
    with open(filename, 'r') as f:
        data = json.load(f)
    a = data["a"]
    b = data["b"]
    a_s = data["a_s"]
    b_s = data["b_s"]
    m = data["m"]
    print(a_s)
    print(b_s)


    def trn(x):
        return 2 * np.pi * ((x - a) / (b - a)) - np.pi
    def f(x):
        x = trn(x)
        return  a_s[0]/2 + sum(a_s[k] * np.cos(k * x) + b_s[k] * np.sin(k * x) for k in range(1, m+1))
    return f

# ---------------- Utils ----------------

# Przycina macierz przechowującą wykres funkcji do okresu (zakładając, że min(x) oraz max(x) to początek i koniec okresu)
def cut_fun(I, y, threshold = 200):
  row = I[y, :]
  xs = np.where(row < threshold)[0]

  I = I[:,np.min(xs):np.max(xs)+1]
  return I

# Normalizuje współrzędne punktów tak by przybliżenie funkcji miało okres 1 oraz y należało do [0,1]
def normalize_points(points):
    delta_w= np.min(points[:,0])
    delta_h = np.min(points[:,1])
    w = np.abs(np.max(points[:,0])-np.min(points[:,0]))
    h = np.abs(np.max(points[:,1])-np.min(points[:,1]))
    norm_points = np.zeros_like(points, dtype=float)
    norm_points[:, 0] = (points[:, 0] - delta_w) / w
    norm_points[:,1] = (points[:, 1] - delta_h) / h

    return norm_points

# Pobiera punkty z obrazu wykresu funkcji
# punkty równooodległe
def get_points(I, n):
    nx = I.shape[1] // n
    points = []
    if nx == 0 : nx += 1
    for k in range(0, I.shape[1], nx):
        col = I[:, k]
        y_idx = np.where(col < 200)[0]
        if len(y_idx) > 0:
            points.append(((np.mean(y_idx) * -1) + (I.shape[0]), k))

    # Wyrównanie końców, żeby spełnić warunek okresowości (y[0]==y[-1])
    border_y = (points[0][1] + points[-1][1]) / 2.
    points[-1] = (border_y,points[-1][0])
    points[0] = (border_y,points[0][0])

    return normalize_points(np.array(points))

# Dekorator nakładany na przybliżaną funkcję
def period(period=1.0, shift=0.0, new_min=0.0, new_max=1.0):
    def decorator(func):
        def wrapper(x):
            x_norm = ((x - shift) / period) % 1.0
            y = func(x_norm)
            return new_min + (new_max - new_min) * y
        return wrapper
    return decorator

# --------------- Aproksymacje ---------------

# Cubic Spline interpolation
def get_cubic_spline(I):
    points = get_points(I, 15)
    points = sorted(points, key=lambda pt: pt[1])

    xs = [x for y, x in points]
    ys = [y for y, x in points]

    assert all(xs[i] < xs[i+1] for i in range(len(xs) - 1)), "x musi być ściśle rosnący"
    assert np.isclose(ys[0], ys[-1]), "Dla bc_type='periodic' wymagane jest y[0] == y[-1]"

    cs = CubicSpline([x for y, x in points], [y for y, x in points], bc_type='periodic')

    @period(period=120, shift=0, new_min=-60, new_max=25)
    def f(x_norm_in_0_1):
        return cs(x_norm_in_0_1)

    return f
    # def save_spline_coefficients(cs, filename='spline_coeffs.json'):
    #   data = {
    #       "x": cs.x.tolist(),
    #       "c": cs.c.tolist()
    #   }
    #   with open(filename, 'w') as f:
    #       json.dump(data, f)
    # save_spline_coefficients(cs)

# Trigonometric Polynomial Approximation
def get_trigonometric_approx(I,m):
    points = get_points(I, I.shape[1]-1)
    points = sorted(points, key=lambda pt: pt[1])

    xs = [x for y, x in points]
    ys = [y for y, x in points]
    n = len(xs)
    a,b = xs[0],xs[-1]

    def trn(x):
        return 2 * np.pi * ((x - a) / (b - a)) - np.pi

    xs = [trn(x) for x in xs]

    a_s = []
    for k in range(m+1):
        a_s.append(2 / n * sum(ys[i] * np.cos(k * xs[i]) for i in range(n)))

    b_s = []
    for k in range(m+1):
        b_s.append(2 / n * sum(ys[i] * np.sin(k * xs[i]) for i in range(n)))

    @period(period=120, shift=0, new_min=-60, new_max=25)
    def f(x):
        x = trn(x)
        return  a_s[0]/2 + sum(a_s[k] * np.cos(k * x) + b_s[k] * np.sin(k * x) for k in range(1, m+1))

    return f
    # def save_prox_coefficients(filename='approx_coeffs.json'):
    #   data = {
    #       "a": a,
    #       "b": b,
    #       "a_s":a_s,
    #       "b_s":b_s,
    #       "m":m
    #   }
    #   with open(filename, 'w') as f:
    #       json.dump(data, f)
    # save_prox_coefficients()

if __name__ == "__main__":
    I = cv2.imread("sa_plot.jpg", cv2.IMREAD_GRAYSCALE)
    if I is None:
        raise FileNotFoundError("Nie znaleziono pliku 'sa_plot.jpg'")
    # cs = get_cubic_spline(I)
    # f = get_trigonometric_approx(I, m=10)
    # y = f(np.linspace(0, 240, 1000))  # dla przykładowych x-ów