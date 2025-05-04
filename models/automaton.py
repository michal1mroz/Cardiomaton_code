from models.cell import Cell
from models.cell_state import CellState

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
    def __init__(self,data_array: np.ndarray, cells: Dict[Tuple[int, int], Cell], frame_time: float = 0.2):
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
        #self.automaton = self._create_automaton_grid(binary_array)
        self.grid_b = self._create_automaton()
        self.frame_time = frame_time
        self.is_running = False
        self.frame_counter = 0

        self.fig = self.ax = self.img = None

    def _create_automaton(self) -> List[Cell]:
        return [value for value in self.cells.values()]


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
            1: CellState.WAITING,
        }
        return np.array([
            [Cell(value_to_state[val]) for val in row] for row in binary_array
        ])    

    def _update_cell(self, cell: Cell) -> Tuple[CellState, bool]:
        """
        Method to update cells state using neigbours.
        For now just cycle through the states if it was polarized. If not, check if
        any neighbour is depolarizing.

        Args:
            position (Tuple[int, int]): indices of a given cell
        
        Returns:
            Tuple[CellState, bool]: New state of the cell and information if it was polarized
        """
        if cell.state == CellState.DEAD:
            return cell.state, False
        # Losing charge
        if cell.state != CellState.WAITING:
            return CellState((cell.state.value + 1) % (len(CellState) - 1)), False
        
        # Check if it can take in charge
        else:
            for nei in cell.neighbours:
                if nei.state == CellState.DEPOLARIZATION:
                    return CellState.POLARIZATION, True
            
        # Check if can self polarize
        if cell.self_polarization and self.frame_counter >= (cell.last_polarized + cell.self_polar_timer): 
            return CellState.POLARIZATION, True 

        # No update
        return cell.state, False

    def update_grid(self) -> None:
        """
        Method to update the grid based on the current state.
        """
        for ind, cell in enumerate(self.grid_a):
            new_state, flag = self._update_cell(cell)
            self.grid_b[ind].state = new_state
            if flag:
                self.grid_b[ind].last_polarized = self.frame_counter
        
        self.grid_a, self.grid_b = self.grid_b, self.grid_a
        
    def _to_numpy(self) -> np.ndarray:
        """
        Simple method to map self.automaton array to array of numbers

        Returns:
            np.ndarray: array of type int from Cell.to_int() method
        """
        #res = np.zeros(self.shape)
        for cell in self.grid_a:
            self.draw_array[cell.position] = cell.to_int()
        return self.draw_array 
        #return np.array([[cell.to_int() for cell in row] for row in self.automaton])

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

        cmap = colors.ListedColormap(['white','gray', 'yellow', 'red', 'blue', 'green', 'black'])
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
 