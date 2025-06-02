import networkx as nx # type: ignore
import numpy as np # type: ignore
from matplotlib import pyplot as plt # type: ignore
from scipy.spatial import cKDTree # type: ignore
from scipy.sparse.csgraph import minimum_spanning_tree # type: ignore
from src.models.cell import Cell
from src.models.cell_state import CellState
from src.models.cell_type import CellType

class Space: #, the final frontier

    def __init__(self, binary_array, root = (0,0)):
        self.primary_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.diagonal_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.root = root
        self.graph = None
        # self.graph, _ = self.capped_neighbours_graph(binary_array)
        #self.capped_neighbours_graph(binary_array)


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
                cell = CellType.create(position=point, cell_type=CellType.AV_NODE,state=CellState.SLOW_DEPOLARIZATION)
            else:
                # cell = Cell(position=point,cell_type=CellType.SA_NODE,durations = CellType.SA_NODE.value["durations"], self_polarization=True)

                # cell = Cell(position=point)
                cell = CellType.create(position=point, cell_type=CellType.BACHMANN)
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
                cells[p].add_neighbour(cells[neighbor])
                weight = np.linalg.norm(np.array(point) - np.array(neighbor))
                G.add_edge(tuple(point), neighbor, weight=weight)
        return G, cells

    def capped_neighbours_graph_from_regions(self,region_dict, junction_pixels, cap=4):
        """
        Tworzy graf z połączonych komórek na podstawie pikseli regionów oraz junctionów.
        Typ komórki (CellType) ustalany na podstawie nazwy regionu lub jako junction.

        Args:
            region_dict (dict[str, list[(x, y)]]): Mapa sekcji do listy punktów.
            junction_pixels (list[(x, y)]): Lista punktów połączeń między regionami.
            cap (int): Maksymalna liczba sąsiadów (domyślnie 4).

        Returns:
            networkx.Graph: graf połączeń
            dict[(x, y), Cell]: mapa pozycji do obiektów Cell
        """

        all_points = []
        cell_types = {}

        # Mapowanie nazw sekcji na CellType
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

        # Dodaj punkty z regionów
        for label, points in region_dict.items():
            ctype = label_to_type.get(label)  # default fallback
            for pt in points:
                cell_types[pt] = ctype
                all_points.append(pt)

        # Dodaj punkty junctionów jako osobny typ
        for pt in junction_pixels:
            cell_types[pt] = CellType.JUNCTION
            all_points.append(pt)

        # Stwórz obiekty Cell
        cells = {}
        for pt in all_points:
            # if cell_types[pt] == None:
            #     # print(pt)
            #     cells[pt] = CellType.create(position=pt, cell_type=CellType.INTERNODAL_MID)
            # else:
            cells[pt] = CellType.create(position=pt, cell_type=cell_types[pt])

        # Ustawienie do przeszukiwania sąsiedztwa
        array_points = np.array(all_points)
        tree = cKDTree(array_points)

        # Tworzenie grafu
        G = nx.Graph()
        for idx, point in enumerate(array_points):
            pt = tuple(point)
            neighbors = []

            # Szukaj najpierw w pion/poziom
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (pt[0] + dx, pt[1] + dy)
                if neighbor in cell_types:
                    neighbors.append(neighbor)
                if len(neighbors) == cap:
                    break

            # Jeśli za mało sąsiadów, szukaj po przekątnej
            if len(neighbors) < cap:
                for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    neighbor = (pt[0] + dx, pt[1] + dy)
                    if neighbor in cell_types:
                        # pomiń przekątne między już podłączonymi
                        if not ((pt[0] + dx, pt[1]) in neighbors and (pt[0], pt[1] + dy) in neighbors):
                            neighbors.append(neighbor)
                    if len(neighbors) == cap:
                        break

            for n in neighbors:
                cells[pt].add_neighbour(cells[n])
                dist = np.linalg.norm(np.array(pt) - np.array(n))
                G.add_edge(pt, n, weight=dist)
        # self.graph = G

        # self.draw()
        return G, cells

    def draw(self):
        """
        Uses pyplot to draw the graph
        """
        pos = {node: (node[1], -node[0]) for node in self.graph.nodes()}
        nx.draw(self.graph, pos, with_labels=False, node_color='red', edge_color='blue', node_size=10, width=0.5)
        plt.show()
