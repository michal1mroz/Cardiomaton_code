from src.models.cell import Cell
from src.models.cell_state import CellState
from src.update_strategies.update_with_timing import UpdateWithTiming
from src.update_strategies.test_update import TestUpdate
from src.models.cell_type import CellType
from src.update_strategies.update_charge import UpdateCharge
from src.update_strategies.update_charge_ms import UpdateChargeMS

import copy
from typing import Dict, List, Tuple
import numpy as np # type: ignore
from matplotlib import colors # type: ignore
import matplotlib.pyplot as plt # type: ignore
from IPython.display import clear_output, display
from time import sleep, time




class Automaton:
    """
    Stores the cell array and controles the simulation.
    is_running (bool): Stops the update on the automaton
    """
    def __init__(self, data_array: np.ndarray, cells: Dict[Tuple[int, int], Cell], frame_time: float = 0.2):
        """
        Automaton constructor.

        frame_time will probably be changed depending on the method used to controle the speed.
        grid_b is a copy of the array created to avoid the overhead of memory allocation and copying on each update.

        Args:
            cells Dict[Tuple[int, int], Cell]: mapping of the cell to a position
            frame_time (float, optional): Frame time in seconds. Defaults to 0.2s.
        """
        self.shape = data_array.shape
        self.draw_array = np.zeros(self.shape)
        self.cells = cells
        self.grid_a = self._create_automaton()
        self.grid_b = self._copy_grid(self.grid_a)
        self.frame_time = frame_time
        self.is_running = False
        self.frame_counter = 0
        # self.update_method = BasicUpdate()
        #self.update_method = UpdateWithTiming()
        # self.update_method = UpdateCharge()
        self.update_method = UpdateChargeMS()
        self.fig = self.ax = self.img = None


    def _create_automaton(self) -> List[Cell]:
        """
        Simple method to flatten the dict of cells (Dict[Tuple[int, int], Cell]) to a list of cells.

        Returns:
            cells (List[Cell]) - flattened list
        """
        return [value for value in self.cells.values()]

    def _copy_grid(self, cell_list: List[Cell]) -> List[Cell]:
        """
        Internal method to copy the grid. Standard deepcopy failed with the references to other cells.

        Args:
            cell_list (List[Cell]): List of input cells.

        Returns:
            result_list (List[Cell]): Coppied list
        """
        arr = []
        help_dict = {}
        for cell in cell_list:
            new_cell = Cell(position=cell.position,cell_data = cell.cell_data, init_state=cell.state,cell_type = cell.cell_type,
                            self_polarization=cell.self_polarization,
                            self_polarization_timer=cell.self_polar_timer)
            if len(new_cell.neighbours) != 0: print("cost tu jest nie tak")
            help_dict[cell.position] = new_cell
            arr.append(new_cell)

        for i, cell in enumerate(cell_list):
            for nei in cell.neighbours:
                pos = nei.position
                arr[i].add_neighbour(help_dict[pos])
        return arr

    def _create_automaton_grid(self, binary_array: np.ndarray) -> np.ndarray:
        """
        Private method that creates an array of Cell instances.

        Args:
            binary_array (np.ndarray): Loaded binary array that was passed to constructor
        
        Returns:
            np.ndarray: Numpy array with coresponding cells
        """
        value_to_state = {
            0: CellState.DEAD,
            1: CellState.POLARIZATION,
        }
        return np.array([
            [Cell(value_to_state[val]) for val in row] for row in binary_array
        ])    

    def update_grid(self) -> None:
        """
        Method to update the grid based on the current state.
        """
        reset_frame_counter = False
        for ind, cell in enumerate(self.grid_a):
            #new_state, flag = self.update_method.update(cell, self.frame_counter)
            new_charge, new_state = self.update_method.update(cell)
            
            #if flag:
            #    reset_frame_counter = True
            
            self.grid_b[ind].state = new_state
            self.grid_b[ind].state_timer = cell.state_timer
            self.grid_b[ind].charge = new_charge
        if reset_frame_counter:
            self.frame_counter = 0

        self.grid_a, self.grid_b = self.grid_b, self.grid_a
        
    def _to_numpy(self) -> np.ndarray:
        """
        Simple method to map self.automaton array to array of numbers

        Returns:
            np.ndarray: array of type int from Cell.to_int() method
        """
        for cell in self.grid_a:
            self.draw_array[cell.position] = cell.to_int()
        return self.draw_array
    
    def to_cell_data(self) -> List[Dict]:#List[List[Tuple[int, bool, str, str]]]:
        """
        Simple method to map self.automaton array to array of tuples storing cell informations
        Returns:
            List[List[Tuple[int, bool, str]]]: A 2D list representing the grid,
            where each element is a tuple with cell information. Positions without a cell
            are filled with None.
        """
        return {cell.position: cell.to_dict() for cell in self.grid_a}

    def recreate_from_dict(self, data: List[Dict]) -> None:
        """
        Method to recreate grid_a, grid_b and cells data from the dict.
        Updates the automaton in place.
        
        Args:
            data (List[Dict]): result of to_cell_data method
        """
        cells_a, cells_b = {}, {}
        for cell_dict in data:
            cells_a.update({cell_dict["position"]: CellType.create(position = cell_dict["position"], cell_type = cell_dict["ccs_part"], state = cell_dict["state_value"])})
            cells_b.update({cell_dict["position"]: CellType.create(position = cell_dict["position"], cell_type = cell_dict["ccs_part"], state = cell_dict["state_value"])})
        
        for cell_dict in data:
            cell_a, cell_b = cells_a[cell_dict["position"]], cells_b[cell_dict["position"]]
            for nei in cell_dict["neighbours"]:
                cell_a.add_neighbour(cells_a[nei])
                cell_b.add_neighbour(cells_b[nei])
        
        self.cells = cells_a
        self.grid_a = cells_a.values()
        self.grid_b = cells_b.values()

    def draw(self, first_time: bool = False) -> None:
        """
        Method to draw the current state of the automaton using matplotlib.
        Used for visualization while working on the model. To be deleted later.

        Args:
            first_time (bool, optional): Needs to be set to True for the plot initialization
        """
        data = self._to_numpy()
        if first_time:
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.set_xticks([])
            self.ax.set_yticks([])

        cmap = colors.ListedColormap(['white','gray', 'yellow', 'red', 'pink', 'green', 'black'])
        bounds = np.arange(-0.5, 7.5, 1)
        norm = colors.BoundaryNorm(bounds, cmap.N)

        self.ax.cla()
        self.ax.imshow(data, cmap=cmap, norm=norm)

        display(self.fig)
        clear_output(wait=True)

    def run_simulation(self):
        """
        Simple method to update the simulation. sleep function is used more for debug than anything since
        it doesn't include the time needed for the update and rendering of the new frame.
        """
        self.draw(first_time=True)

        while True:
            self.frame_counter += 1
            sleep(self.frame_time)
            self.update_grid()
            self.draw()

    def run_test_signal(self, trigger_position: Tuple[int, int]):
        """
        Runs a single depolarization wave through the grid to measure signal propagation.

        The simulation stops when no further state changes occur. This allows assessment of how far 
        (depth) and how long (duration in frames) the signal travels through the graph.

        Returns:
            Tuple[int, int]: Maximum depth reached and total number of frames until signal propagation ends.
        """
         
        tmp_grid = self._copy_grid(self.grid_a)
        test_grid = self.grid_a
        
        for cell in test_grid:
            cell.state = CellState.POLARIZATION
            cell.activated_at = None

        for cell in test_grid:
            if cell.position == trigger_position:
                cell.state = CellState.RAPID_DEPOLARIZATION
                cell.activated_at = 0
                break

        frame_counter = 0

        self.draw(first_time=True)
        while True:
            sleep(self.frame_time)
            updated = False
            next_states = []

            for cell in test_grid:
                new_state, depolarized = TestUpdate().update(cell, frame_counter)
                next_states.append((cell, new_state, depolarized))
                if depolarized and cell.activated_at is None:
                    cell.activated_at = frame_counter
                if cell.state != new_state:
                    updated = True
            
            for cell, new_state, _ in next_states:
                cell.state = new_state

            self.draw()

            if not updated:
                break
            frame_counter += 1

        max_depth = max(
            (cell.activated_at for cell in test_grid if cell.activated_at is not None),
            default=-1
        )

        self.grid_a = tmp_grid
        return max_depth, frame_counter
