from src.utils.image_loader import *
from src.models.cell_type import ConfigLoader
from src.utils.graph_builder import extract_conduction_pixels
from src.models.cellular_graph import Space
from src.models.automaton import Automaton
from src.database.db import *
from src.database.crud.automaton_crud import *
from src.database.utils.cell_utils import *
from src.database.models.automaton_cell_args import *
from src.database.models.cell_arguments import *

cell_data = {
    frozenset({
        "V_rest":-60.0, 
        "V_thresh":-60.0, 
        "V_peak":15.0,
        "t_thresh":0.5, 
        "t_peak":0.45, 
        "t_end":0.95,
        "eps":0.01,
        "period":1.2,
        "range": 200
    }.items()): 1,
    frozenset({
        "V_rest":-60.0, 
        "V_thresh":-40.0, 
        "V_peak":15.0,
        "t_thresh":0.35, 
        "t_peak":0.45, 
        "t_end":0.80,
        "eps":0.005,
        "period":0.8,
        "range": 200
    }.items()): 2
}

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ConfigLoader.loadConfig()
    graph, A, B = extract_conduction_pixels()
    space = Space(graph)
    _, cell_map = space.build_capped_neighbours_graph_from_regions(A, B, cap=8)

    automaton = Automaton(graph.shape, cell_map, frame_time=0.1)
    init_db()
    db = SessionLocal()
    # res = create_or_overwrite_entry(db, "default", automaton.grid_a, graph.shape[0], graph.shape[1], 10)
    # print(res)
    aut = get_automaton(db, "default")
    print(aut.frame_counter)