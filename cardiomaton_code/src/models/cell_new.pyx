from src.models.cell_state import CellState

cdef class Cell:

    def __init__(self, tuple[int,int] position, object cell_type, dict cell_data,
                 object init_state = None,
                 bint self_polarization = False,
                 int self_polarization_timer = 0):

        if init_state is None:
            from src.models.cell_state import CellState
            init_state = CellState.POLARIZATION
        self_polar_threshold = 200
        self.state = init_state
        self.self_polarization = self_polarization
        self.cell_type = cell_type
        self.self_polar_timer = self_polarization_timer
        self.state_timer = 0
        self.position = position
        self.neighbours = []
        self.charge = 0
        self.cell_data = cell_data

    cpdef reset_timer(self):
        self.state_timer = 0

    cpdef update_timer(self):
        self.state_timer += 1

    cpdef reset_self_polar_timer(self):
        self.self_polar_timer = 0

    cpdef update_self_polar_timer(self):
        self.self_polar_timer += 1

    cpdef add_neighbour(self, Cell neighbour):
        self.neighbours.append(neighbour)

    cpdef double to_int(self):
        return self.state.value + 1

    cpdef tuple to_tuple(self):
        return (self.state.value + 1,
                self.self_polarization,
                self.state.name.capitalize(),
                self.cell_type.value["name"],
                self.charge)

    cpdef update_data(self,dict data_dict):
        self.state = CellState(int(data_dict['state_value']))
        if self.state == CellState.RAPID_DEPOLARIZATION:
            self.charge = self.cell_data.get('peak_potential', 0)

    cpdef get_color(self):
        return {
            CellState.POLARIZATION: 'gray',
            CellState.RAPID_DEPOLARIZATION: 'yellow',
            CellState.SLOW_DEPOLARIZATION: 'pink',
            CellState.REPOLARIZATION: 'red',
            CellState.DEAD: 'black',
            }[self.state]

    cpdef to_dict(self):
        return {
            "position": self.position,
            "state_value": self.state.value + 1,
            "state_name": self.state.name.capitalize(),
            "charge": self.charge,
            "ccs_part": self.cell_type.value,
            "cell_type": self.cell_type.name,
            "auto_polarization": self.self_polarization,
        }