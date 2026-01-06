from src.backend.enums.cell_type import ConfigLoader
from src.utils.graph_builder import extract_conduction_pixels
from src.models.cellular_graph import Space
from src.database.db import *
from src.database.crud.automaton_crud import *

if __name__ == '__main__':

    configurations = {
        "PHYSIOLOGICAL" : "resources/data/cell_data.json",
        "SINUS_BRADYCARDIA" : "resources/data/sinus_bradycardia.json",
        "SINUS_TACHYCARDIA": "resources/data/sinus_tachycardia.json",
        "AV_BLOCK_I": "resources/data/av_block_i.json",
        "SINUS_PAUSE_RETROGRADE": "resources/data/sinus_pause_retrograde.json",
        "SA_BLOCK_RETROGRADE": "resources/data/sa_block_retrograde.json",
    }

    init_db()
    db = SessionLocal()

    for config_name, config_path in configurations.items():
        ConfigLoader.loadConfig(config_path)
        graph, A, B = extract_conduction_pixels()
        space = Space(graph)
        _, cell_map = space.build_capped_neighbours_graph_from_regions(A, B, cap=8)
        res = create_or_overwrite_entry(db, config_name, cell_map.values(), graph.shape[0], graph.shape[1], 1100, is_preset=True)

    