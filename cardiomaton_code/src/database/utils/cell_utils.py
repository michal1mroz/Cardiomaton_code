from typing import Any, Dict, List, Tuple
import numpy as np

from cardiomaton_code.src.models.cell import Cell
from src.models.cell_state import CellState
from src.models.cell_type import CellType

"""
    This module provides the functions needed to serialize and deserialize the cells into/from the binary blob.

    Deserialization returns a list of cell_dtype that needs additional handling - especially handling for the neighbors -
    before they can be used
"""

##############################################################################
# Cell parameters serialization

_CELL_TYPE_TO_INT = {ct: i for i,ct in enumerate(CellType)}
_INT_TO_CELL_TYPE = {i: ct for i, ct in enumerate(CellType)}

def pack_enums(state: CellState, type: CellType, self_polar: bool) -> np.uint8:
    """
        Pack state, type and self_polarization flag into 1 byte unsigned int

        Args:
            state: CellState - state of the cell
            type: CellType - type of the cell
            self_polar: bool - self_polarization flag of the cell

        Returns:
            np.uint8 - encoded uint with:
                first 3 bits - state
                another 4 bits - type
                last 1 bit - self_polarization flag
    """
   
    val = (state.value & 0b111)
    val |= (_CELL_TYPE_TO_INT[type] & 0b1111) << 3
    val |= (1 if self_polar else 0) << 7
    return np.uint8(val)

def unpack_enums(num: np.uint8) -> Tuple[CellState, CellType, bool]:
    """
        Unpacks the np.uint8 with state, type and self_polarization values
        to objects.

        Args:
            num: np.uint8 - bit encoded number.
        
        Returns:
            CellState - encoded state
            CellType - encoded type
            bool - self polarization flag
    """
    state_val = num & 0b111
    cell_type_val = (num >> 3) & 0b1111
    flag = bool((num >> 7) & 1)
    return CellState(state_val), CellType(_INT_TO_CELL_TYPE[cell_type_val]), flag

_ENC_NEI = {-1: 0, 0: 1, 1: 2}
_DEC_NEI = (-1, 0, 1)

def pack_neighbors(neighbors: List[Tuple[int, int]]) -> np.uint32:
    """
        Encodes the relative positions of neighbors into uint32. Assumes that
        there are at most 8 neighbors possible.

        Args:
            neighbors: List[Tuple[int, int]] - list of relative positions of neighbors
        
        Returns:
            uint32 - number with encoded positions
    """
    code = 0
    for i, (dx, dy) in enumerate(neighbors):
        dx_code = _ENC_NEI[dx] & 0x3
        dy_code = _ENC_NEI[dy] & 0x3
        nib = dx_code | (dy_code << 2)
        code |= (nib & 0xF) << (4 * i)
    return np.uint32(code)

def unpack_neighbors(code: np.uint32, n: int) -> List[Tuple[int, int]]:
    """
        Decodes the relative positions of neighbors from uint32.

        Args:
            code: np.uint32 - number with encoded neighbors
            n: int - number of neighbors encoded

        Returns:
            List[Tuple[int, int]] - list of neighbors relative positions
    """
    code = int(code)
    out = []
    for i in range(n):
        nib = (code >> (4 *i)) & 0xF
        dx = _DEC_NEI[nib & 0x3]
        dy = _DEC_NEI[(nib >> 2) & 0x3] 
        out.append((dx, dy))
    return out

################################################################################
# Cell object serialization

cell_dtype = np.dtype([
    ("flags", np.uint8),
    ("charge", np.float32),
    ("position", np.int16, (2,)),
    ("neighbors", np.uint32),
    ("n_neighbors", np.uint8),
    ("arg_id", np.int32),
])

def encode_cell(cell: Cell, arg_id: np.int32) -> np.void:
    """
        Encodes a single cell into cell_dtype object.
        
        Args:
            cell: Cell - cell to be encoded
            arg_id np.int32: id of the cell_data row in cell_arguments table
        
        Returns:
            np.void - encoded cell
    """
    return np.array((
            pack_enums(cell.state, cell.cell_type, cell.self_polarization),
            np.float32(cell.charge),
            np.array(cell.position, dtype=np.int16),
            pack_neighbors(cell.neighbors_to_ints()),
            np.uint8(len(cell.neighbours)),
            np.int32(arg_id)),
        dtype=cell_dtype)[()]

def decode_cell(blob: np.void, cell_args) -> Tuple[Cell, List[Tuple[int, int]]]:
    """
        Decodes blob to a single cell and a list of neighbors in relative position

        Args:
            blob: np.void - array of type cell_dtype with encoded cell data
        
        Returns:
            Cell - decoded cell without neighbors
            List[Tuple[int, int]] - list of neighbors
    """
    
    state, cell_type, self_polar = unpack_enums(blob["flags"])
    position = tuple(blob["position"])
    neighbors = list(map(lambda x: (position[0] - x[0], position[1] - x[1]), unpack_neighbors(blob["neighbors"], blob["n_neighbors"])))
    arg_id = blob["arg_id"]
    cell = Cell(position = position, cell_type=cell_type, cell_data=cell_args[arg_id], init_state=state, self_polarization=self_polar)
    cell.charge = float(blob["charge"])
    return cell, neighbors

def serialize_cells(cells: List[Cell], arg_dict: Dict) -> bytes:
    """
        Function that serializes a list of cells to a byte array.

        Args:
            cells List[Cell]: list of cells to be encoded
            arg_dict Dict: dictionary that maps frozenset(cell_data.items()) keys to the database id
        
        Returns:
            bytes - a byte array with encoded cells
    """
    n = len(cells)
    if n == 0:
        return b""
    
    arr = np.empty(n, dtype=cell_dtype)
    for i, c in enumerate(cells):
        encoded = encode_cell(c, arg_dict[frozenset(c.cell_data.items())])
        if isinstance(encoded, np.ndarray):
            arr[i] = encoded[0]
        else:
            arr[i] = encoded

    return arr

def deserialize_cells(blob: bytes) -> List[np.ndarray[Any]]:
    """
        Function that deserializes a byte blob to the list of cell_dtype objects

        Args:
            blob: bytes - encoded binary blob

        Returns: 
            List[np.ndarray[Any]] - List of cell_dtype objects
    """
    if not blob:
        return None    
    return np.frombuffer(blob, dtype=cell_dtype)