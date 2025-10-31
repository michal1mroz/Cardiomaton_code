from src.utils.image_loader import *
import numpy as np
from src.update_strategies.charge_approx.pacemakers import pacemaker_AP

cell_data =  {
            "V_rest":-60,
            "V_thresh":-40,
            "V_peak":10,
            "t40":120 / 1000,
            "t03":128 / 1000,
            "t34":308 / 1000,
            "eps":0.01
        }
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    tab = np.linspace(0, 0.278, 200)
    print(tab)
    n_range = 600
    a = 0.279 / n_range
    V = [pacemaker_AP((t % n_range) * a, **cell_data) for t in list(range(n_range))]
    print(V)