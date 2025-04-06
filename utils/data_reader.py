import json
import cv2
import numpy as np
from models.cellular_graph import Space

BASE_NODES_NR = 5997
BASE_ROOT = (50, 22)

def load_to_binary_array(path: str, nr_of_nodes: int = BASE_NODES_NR) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    ccs = (img > 15).astype(np.int_)

    scale = np.sqrt(nr_of_nodes / BASE_NODES_NR) * 0.876 # Co to za liczba???

    ccs = ccs.astype(np.float32)
    ccs = cv2.resize(ccs, (0, 0), fx=scale, fy=scale)

    return (ccs > 0).astype(np.int_)

def img_graph(path: str, nr_of_nodes: int = BASE_NODES_NR) -> Space:
    scale = np.sqrt(nr_of_nodes / BASE_NODES_NR) * 0.876
    return Space(load_to_binary_array(path, nr_of_nodes), (BASE_ROOT[0] * scale, BASE_ROOT[1] * scale))
