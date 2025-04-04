import json
import cv2
import numpy as np
from models.cellular_graph import Space

BASE_NODES_NR = 5997
BASE_ROOT = (50, 22)

def img_graph(path, nr_of_nodes = 5997):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    ccs = (img > 15).astype(np.int_)

    scale = np.sqrt(nr_of_nodes / BASE_NODES_NR) * 0.876

    ccs = ccs.astype(np.float32)
    ccs = cv2.resize(ccs, (0, 0), fx=scale, fy=scale)

    binary_array = (ccs > 0).astype(np.int_)

    return Space(binary_array, (BASE_ROOT[0] * scale, BASE_ROOT[1] * scale))
