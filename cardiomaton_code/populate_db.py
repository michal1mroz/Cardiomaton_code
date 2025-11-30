from src.backend.enums.cell_type import ConfigLoader
from src.utils.graph_builder import extract_conduction_pixels
from src.models.cellular_graph import Space
from src.database.db import *
from src.database.crud.automaton_crud import *

if __name__ == '__main__':
    ConfigLoader.loadConfig()
    graph, A, B = extract_conduction_pixels()
    space = Space(graph)
    _, cell_map = space.build_capped_neighbours_graph_from_regions(A, B, cap=8)

    init_db()
    db = SessionLocal()
    res = create_or_overwrite_entry(db, "default", cell_map.values(), graph.shape[0], graph.shape[1], 0)