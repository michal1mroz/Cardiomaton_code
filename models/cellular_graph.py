import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import cKDTree
from scipy.sparse.csgraph import minimum_spanning_tree


class Space:
    def __init__(self, binary_array, root= (50, 22)):
        self.graph = self.create_graph_from_matrix(binary_array, root)
    def create_graph_from_matrix(self,binary_array,root, return_mst = False):
        points = np.argwhere(binary_array == 1)

        # Stwórz k-d tree dla szybkiego wyszukiwania sąsiadów
        tree = cKDTree(points)

        # Znajdź sąsiadów w promieniu sqrt(2), czyli do 8 sąsiadów
        indices = tree.query_ball_point(points, np.sqrt(2))

        # Utwórz graf ważony
        G = nx.Graph()
        for i, neighbors in enumerate(indices):
            for j in neighbors:
                if i != j:  # Unikaj pętli
                    p1, p2 = points[i], points[j]
                    weight = np.linalg.norm(p1 - p2)
                    G.add_edge(tuple(p1), tuple(p2), weight=weight)

        # Znajdź minimalne drzewo rozpinające zaczynając od danego korzenia
        if not return_mst:
            return G
        mst = nx.minimum_spanning_tree(G)

        # Konwertuj MST na drzewo ukorzenione w zadanym wierzchołku
        if root in mst.nodes:
            mst = nx.bfs_tree(mst, root)
        else:
            print(f"Warning: Root {root} not found in MST nodes.")

        return mst.to_undirected()


    def draw(self):
        pos = {node: (node[1], -node[0]) for node in self.graph.nodes()}
        nx.draw(self.graph, pos, with_labels=False, node_color='red', edge_color='blue', node_size=10, width=0.5)
        plt.show()
