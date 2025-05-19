import json
import cv2
import numpy as np
from typing import Tuple
from src.models.cellular_graph import Space

def load_to_binary_array(path : str = "./resources/img_ccs/", nr_of_nodes: int = 1500) -> Tuple[np.ndarray, Tuple[float, float]]:
    """
    Loads a binary array representing the cardiac conduction system from an image.

    Args:
        path (str): Path to the directory containing the **CCS.png** image and **CCS_info.json** metadata file.
        nr_of_nodes (int): Desired number of nodes to represent the CCS. Used for scaling the image.

    Returns:
        Tuple[np.ndarray, Tuple[int, int]]:
            - A binary NumPy array (1: part of CCS, 0: background).
            - A tuple representing the (y, x) position of the AV node in the binary array.
    """
    img = cv2.imread(path + "CCS.png", cv2.IMREAD_GRAYSCALE)
    ccs = (img > 15).astype(np.int_)

    with open(path + "CCS_info.json") as img_info:
        data = json.load(img_info)
        base_nr_of_nodes = data["base_nodes_number"]
        AV_node_position = data["AV_node_position"]

    scale = np.sqrt(nr_of_nodes/base_nr_of_nodes) * ccs.shape[0]/ccs.shape[1]

    ccs = ccs.astype(np.float32)
    ccs = cv2.resize(ccs, (0, 0), fx=scale, fy=scale)

    AV_node_position = np.multiply(AV_node_position,scale).astype(np.int_)

    return (ccs > 0).astype(np.int_), tuple(AV_node_position)

def img_graph(path : str = "../resources/img_ccs/", nr_of_nodes: int = 1500) -> Space:
    """
    Loads a binary array representing the cardiac conduction system from an image.

    Args:
        path (str): Path to the directory containing the **CCS.png** image and **CCS_info.json** metadata file.
        nr_of_nodes (int): Desired number of nodes to represent the CCS. Used for scaling the image.

    Returns:
        Space: Class used to represent CCS as graph
        """
    binary_array, av_pos = load_to_binary_array(path = path,nr_of_nodes = nr_of_nodes)
    return Space(binary_array, av_pos)

