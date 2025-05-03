import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import cKDTree
from scipy.sparse.csgraph import minimum_spanning_tree


class Space: #, the final frontier

    def __init__(self, binary_array, root):
        self.primary_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.diagonal_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.root = root
        self.graph = self.capped_neighbours_graph(binary_array)


    def nearest_neighbours_graph(self,binary_array: np.ndarray):
        """
        Creates the graph where cells are connected if they are in sqrt(2) radius - maximum of 8 neighbours.
        One of the ways to create cells neighborhood.
        binary_array (np.ndarray): Binary array with cell positions. Result of `load_to_binary_array()` from utils.data_reader
        """
        points = np.argwhere(binary_array == 1)

        # Create k-d tree to search neighbours faster
        tree = cKDTree(points)

        # Search for neighbours in radius sqrt(2)
        indices = tree.query_ball_point(points, np.sqrt(2))

        G = nx.Graph()
        for i, neighbors in enumerate(indices):
            for j in neighbors:
                if i != j:
                    p1, p2 = points[i], points[j]
                    weight = np.linalg.norm(p1 - p2)
                    G.add_edge(tuple(p1), tuple(p2), weight=weight)

        return G

    def capped_neighbours_graph(self, binary_array, cap = 4):
        """
        Creates the graph where maximum of cap cells are connected if they are in sqrt(2) radius - maximum of 8
        neighbours. Prioritising cells arranged vertically or horizontally.
        One of the ways to create cells neighborhood.
        binary_array (np.ndarray): Binary array with cell positions. Result of `load_to_binary_array()` from utils.data_reader
        """

        points = np.argwhere(binary_array == 1)

        # Create k-d tree for faster neighbour search
        tree = cKDTree(points)

        # find 8 neighbours of node
        indices = tree.query_ball_point(points, np.sqrt(2))

        # Create weighted graph
        G = nx.Graph()

        for point in points:
            neighbors = []

            # Check 4-connected neighbors
            for dx, dy in self.primary_dirs:
                neighbor = (point[0] + dx, point[1] + dy)
                if binary_array[neighbor[0], neighbor[1]] > 0:
                    neighbors.append(neighbor)
                if len(neighbors) == cap:
                    break
            # Add diagonal neighbors if less than 4
            if len(neighbors) < cap:
                for dx, dy in self.diagonal_dirs:
                    neighbor = (point[0] + dx, point[1] + dy)
                    if not ((point[0] + dx, point[1]) in neighbors and (point[0], point[1] + dy) in neighbors):
                        if binary_array[neighbor[0], neighbor[1]] > 0:
                            neighbors.append(neighbor)
                        if len(neighbors) == 4:
                            break

            for neighbor in neighbors:
                weight = np.linalg.norm(np.array(point) - np.array(neighbor))
                G.add_edge(tuple(point), neighbor, weight=weight)

        return G

    def draw(self):
        """
        Uses pyplot to draw the graph
        """
        pos = {node: (node[1], -node[0]) for node in self.graph.nodes()}
        nx.draw(self.graph, pos, with_labels=False, node_color='red', edge_color='blue', node_size=10, width=0.5)
        plt.show()
