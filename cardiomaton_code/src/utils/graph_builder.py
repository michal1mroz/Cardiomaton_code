import cv2
import numpy as np
from src.models.cellular_graph import Space
from itertools import chain
from scipy.spatial import KDTree

def img_graph(path : str = "./resources/img_ccs/", nr_of_nodes: int = 1500) -> Space:
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

def extract_conduction_pixels(path = "./resources/img_ccs/",nr_of_nodes = 1500,threshold= 127, min_component_size = 30):
    """

    Args:
        path:
        nr_of_nodes:
        threshold:
        min_component_size:

    Returns:
        bin_main - A binary NumPy array (1: part of CCS, 0: background).
        region_dict - dictionary in which keys are CCS parts names and points ( x,y coordinates) as values
        junction_pixels - list of junction cells
    """
    THRESHOLD_MAIN_IMAGE = 127
    THRESHOLD_PARTS_IMAGE = 110
    def binarize_image(image_path, threshold):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, bin_img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        return bin_img

    def get_connected_components(binary_img):
        # Find connected components using 8-connectivity
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_img, connectivity=8)
        components = []
        x = 0
        for label in range(1, num_labels+1):  # skip background
            component_mask = labels == label
            if np.sum(component_mask) < min_component_size: continue
            points = list(zip(*np.where(component_mask)))
            components.append(points)
        return components

    # Binarize images
    bin_main = binarize_image(path + "CCS.png", THRESHOLD_MAIN_IMAGE)
    bin_parts = binarize_image(path + "CCS_parts.png", THRESHOLD_PARTS_IMAGE)

    # Get main graph components (full system) and parts (regions)
    region_components = get_connected_components(bin_parts)

    # Order in which they are read
    labels = [
        "bachmann", "his_right", "sa_node", "internodal_ant",
        "internodal_post", "internodal_mid", "his_bundle", "av_node", "his_left"
    ]
    region_dict = dict(zip(labels, region_components))

    region_pixels = set(chain.from_iterable(region_components))

    # find pixels which belongs to whole mesh, but does not to specific part : junctions
    all_pixels = set(zip(*np.where(bin_main == 255)))
    junction_pixels = list(all_pixels - region_pixels)

    # build KDTree to search for the closest point
    region_kdtrees = {
        label: KDTree(points)
        for label, points in region_dict.items()
    }
    for pixel in junction_pixels:
        min_dist = float('inf')
        closest_label = None

        for label, kdtree in region_kdtrees.items():
            dist, _ = kdtree.query(pixel)
            if dist < min_dist:
                min_dist = dist
                closest_label = label
        if closest_label:
            region_dict[closest_label].append(pixel)

    return bin_main, region_dict, []