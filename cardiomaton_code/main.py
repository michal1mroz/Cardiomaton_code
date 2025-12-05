from src.utils.image_loader import *
from src.backend.enums.cell_type import ConfigLoader
from src.utils.graph_builder import extract_conduction_pixels
from src.models.cellular_graph import Space
from src.database.db import *
from src.database.crud.automaton_crud import *
from src.database.utils.cell_utils import *
from src.database.models.automaton_cell_args import *
from src.database.models.cell_arguments import *

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ConfigLoader.loadConfig()
    graph, A, B = extract_conduction_pixels()
    space = Space(graph)
    _, cell_map = space.build_capped_neighbours_graph_from_regions(A, B, cap=8)

    # automaton = Automaton(graph.shape, cell_map, frame_time=0.1)
    init_db()
    db = SessionLocal()
    print("test")
    # res = create_or_overwrite_entry(db, "default", cell_map.values(), graph.shape[0], graph.shape[1], 10)
    # print(res)
    # res = create_or_overwrite_entry(db, "default2", cell_map.values(), graph.shape[0], graph.shape[1], 10)
    # res = create_or_overwrite_entry(db, "default3", cell_map.values(), graph.shape[0], graph.shape[1], 10)
   
   
    # aut = get_automaton(db, "default")
    # print(aut)

    # print(list_entries(db))
    # print(delete_entry(db, "default"))
    print(list_entries(db))
