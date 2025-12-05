import networkx as nx # type: ignore
import numpy as np # type: ignore
from matplotlib import pyplot as plt # type: ignore
from scipy.spatial import cKDTree # type: ignore
from scipy.sparse.csgraph import minimum_spanning_tree # type: ignore

#from src.models.cell_state import CellState
from src.backend.enums.cell_state import CellState
from src.backend.models.cell import Cell
from src.backend.enums.cell_type import CellType
# from src.models.cell_type import CellType

class Space: #, the final frontier

    def __init__(self, binary_array, root = (0,0)):
        self.primary_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.diagonal_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.root = root
        self.graph = None

    def build_nn_graph(self, binary_array: np.ndarray):
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

    def build_capped_neighbours_graph(self, binary_array, cap = 4):
        """
        Creates the graph where maximum of cap cells are connected if they are in sqrt(2) radius - maximum of 8
        neighbours. Prioritising cells arranged vertically or horizontally.
        One of the ways to create cells neighborhood.

        Args:
            binary_array (np.ndarray): Binary array with cell positions. Result of `load_to_binary_array()` from utils.data_reader
        
        returns:
            networkx graph
            cells_map dict[Tuple[int, int], Cell] - dict mapping position in the grid to a given cell
        """

        points = np.argwhere(binary_array == 1)
        # Create k-d tree for faster neighbour search
        cells = {}
        for p in points:
            point = (p[0], p[1])
            cell = None
            if point == self.root:
                cell = Cell(position=point, cell_type=CellType.AV_NODE,state=CellState.SLOW_DEPOLARIZATION)
 
                #CellType.create(position=point, cell_type=CellType.AV_NODE,state=CellState.SLOW_DEPOLARIZATION)
            else:
                cell = Cell(position=point, cell_type=CellType.BACHMANN)

                # CellType.create(position=point, cell_type=CellType.BACHMANN)

            cells[point] = cell

        tree = cKDTree(points)

        # find 8 neighbours of node
        indices = tree.query_ball_point(points, np.sqrt(2))

        # Create weighted graph
        G = nx.Graph()
        rows, cols = binary_array.shape

        for ind, point in enumerate(points):
            neighbors = []

            # Check 4-connected neighbors
            for dx, dy in self.primary_dirs:
                neighbor = (point[0] + dx, point[1] + dy)
                if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                    if binary_array[neighbor[0], neighbor[1]] > 0:
                        neighbors.append(neighbor)
                if len(neighbors) == cap:
                    break
            # Add diagonal neighbors if less than 4
            if len(neighbors) < cap:
                for dx, dy in self.diagonal_dirs:
                    neighbor = (point[0] + dx, point[1] + dy)
                    if not ((point[0] + dx, point[1]) in neighbors and (point[0], point[1] + dy) in neighbors):
                        if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                            if binary_array[neighbor[0], neighbor[1]] > 0:
                                neighbors.append(neighbor)
                        if len(neighbors) == 4:
                            break

            p = (point[0], point[1])
            for neighbor in neighbors:
                cells[p].add_neighbor(cells[neighbor])
                weight = np.linalg.norm(np.array(point) - np.array(neighbor))
                G.add_edge(tuple(point), neighbor, weight=weight)
        return G, cells

    def build_capped_neighbours_graph_from_regions(self, region_dict, junction_pixels, cap=4):
        """
        Creates a graph of connected cells based on region pixels and junctions. The cell type (CellType) is determined
        by the region name or as a junction.

        Args:
            region_dict (dict[str, list[(x, y)]]): Map of sections to a list of points.
            junction_pixels (list[(x, y)]): List of connection points between regions.
            cap (int): Maximum number of neighbors (default 4).

        Returns:
            networkx.Graph: Connection graph
            dict[(x, y), Cell]: Map of positions to Cell objects
        """

        all_points = []
        cell_types = {}

        # Maping cell
        label_to_type = {
            "sa_node": CellType.SA_NODE,
            "av_node": CellType.AV_NODE,
            "his_bundle": CellType.HIS_BUNDLE,
            "his_left": CellType.HIS_LEFT,
            "his_right": CellType.HIS_RIGHT,
            "bachmann": CellType.BACHMANN,
            "internodal_ant": CellType.INTERNODAL_ANT,
            "internodal_post": CellType.INTERNODAL_POST,
            "internodal_mid": CellType.INTERNODAL_MID
        }

        # Adding points from known regions
        for label, points in region_dict.items():
            ctype = label_to_type.get(label)
            for pt in points:
                cell_types[pt] = ctype
                all_points.append(pt)

        # Adding Junction type cells; outdated, left for safety measures
        for pt in junction_pixels:
            cell_types[pt] = CellType.JUNCTION
            all_points.append(pt)

        # Creating Cell objects
        cells = {}
        for pt in all_points:
            cells[pt] = Cell(position=pt, cell_type=cell_types[pt])
            #CellType.create(position=pt, cell_type=cell_types[pt])

        # array for searching neighbours
        array_points = np.array(all_points)

        G = nx.Graph()
        for idx, point in enumerate(array_points):
            pt = tuple(point)
            neighbors = []

            # Horizontal/vertical first
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (pt[0] + dx, pt[1] + dy)
                if neighbor in cell_types:
                    neighbors.append(neighbor)
                if len(neighbors) == cap:
                    break

            # Diagonally second
            if len(neighbors) < cap:
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    neighbor = (pt[0] + dx, pt[1] + dy)
                    if neighbor in cell_types:
                        if not ((pt[0] + dx, pt[1]) in neighbors and (pt[0], pt[1] + dy) in neighbors):
                            neighbors.append(neighbor)
                    if len(neighbors) == cap:
                        break

            for n in neighbors:
                cells[pt].add_neighbor(cells[n])
                dist = np.linalg.norm(np.array(pt) - np.array(n))
                G.add_edge(pt, n, weight=dist)
        return G, cells

    def draw(self):
        """
        Uses pyplot to draw the graph
        """
        pos = {node: (node[1], -node[0]) for node in self.graph.nodes()}
        nx.draw(self.graph, pos, with_labels=False, node_color='red', edge_color='blue', node_size=10, width=0.5)
        plt.show()
