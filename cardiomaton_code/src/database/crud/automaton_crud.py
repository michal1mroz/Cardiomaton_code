from typing import Optional, Dict, Any, Callable, List, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import numpy as np

from src.backend.models.automaton import Automaton
from src.backend.models.cell import Cell

from src.database.models.automaton_cell_args import AutomatonCellArgs
from src.database.models.cell_arguments import CellArguments
from src.database.models.automaton import AutomatonTable
from src.database.utils.cell_utils import deserialize_cells, decode_cell, cell_dtype, encode_cell

from src.database.dto.automaton_dto import AutomatonDto


"""
    Right now this module contains the definitions for most crud operations on the database that might be useful
    in the project.
"""

def get_or_create_cell_arguments(db: Session,
                                 cell_data_dict: Dict[str, Any]) -> int:
    """
    Get or create for a set of cell arguments. First performs the query on the first layer of the
    dict and then filters the result on the contents of the cell_data dictionary.
    Returns the id of the corresponding entry (either created or already existing one)
    """
    flat = {
        'period': cell_data_dict['period'],
        'range': cell_data_dict['range'],
        'propagation_time': cell_data_dict['propagation_time'],
        'propagation_time_max': cell_data_dict['propagation_time_max'],
        'self_polarization': cell_data_dict['self_polarization'],
        'charge_function': cell_data_dict['charge_function'],
        'name': cell_data_dict['name']
    }
    
    stmt = select(CellArguments).filter_by(**flat)
    existing = db.execute(stmt).scalars().first()
    if existing:
        existing_data = existing.get_cell_data()
        if existing_data == cell_data_dict['cell_data']:
            return existing.id
    
    new_row = CellArguments(**flat)
    new_row.set_cell_data(cell_data_dict['cell_data'])

    db.add(new_row)
    db.flush()
    return new_row.id

def create_config_key(cell_config: Dict[str, Any]) -> tuple:
    """Create a unique tuple key from cell_config that handles nested dictionaries"""
    key_parts = []
    
    for field in ['period', 'range', 'self_polarization', 'charge_function', 'name']:
        key_parts.append((field, cell_config.get(field)))
    
    cell_data = cell_config.get('cell_data', {})
    if cell_data:
        sorted_cell_data = sorted(cell_data.items())
        key_parts.append(('cell_data', tuple(sorted_cell_data)))
    
    return tuple(key_parts)

def serialize_cells(cells: List[Cell], arg_dict: Dict) -> bytes:
    """
        Moved from the cell_utils due to the dependency problems.
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
        encoded = encode_cell(c, arg_dict[create_config_key(c.config)])
        if isinstance(encoded, np.ndarray):
            arr[i] = encoded[0]
        else:
            arr[i] = encoded

    return arr

def create_or_overwrite_entry(
        db: Session,
        name: str,
        cells: List[Cell],
        width: int,
        height: int,
        frames: int,
) -> AutomatonTable:
    """
        Creates a new automaton entry. If the entry under the specified name already exists it is overwritten.
        Returns the table schema object that was created.

        Args:
            db: Session - database session
            name: str - string with entries name
            cells: List[Cell] - list of cells defining the automaton
            width: int - width of the automaton grid
            height: int - height of the automaton grid
            frames: int - value of the frame counter from the automaton

        Returns:
            AutomatonTable - created automaton table
    """
    mapping: Dict[tuple, int] = {}
    for cell in cells:
        frozen = create_config_key(cell.config)
        if frozen not in mapping:
            arg_id = get_or_create_cell_arguments(db, cell.config)
            mapping[frozen] = arg_id

    blob = serialize_cells(cells, mapping)
    existing = db.query(AutomatonTable).filter(AutomatonTable.name == name).one_or_none()

    if existing is not None:
        db.query(AutomatonCellArgs).filter_by(automaton_id=existing.id).delete()
        db.delete(existing)
        db.flush()

    row = AutomatonTable(
        name = name,
        data = blob,
        width = width,
        height = height,
        frames = frames,
    )
    db.add(row)
    db.flush()

    arg_ids = set(mapping.values())
    joiners = [AutomatonCellArgs(automaton_id = row.id, arg_id = aid) for aid in arg_ids]
    db.bulk_save_objects(joiners)

    db.commit()
    return row


def get_entry(
        db: Session,
        name: str,
        include_blob: bool = True
) -> Optional[Dict[str, Any]]:
    """
        Returns a simple automaton entry from the database

        Args:
            db: Session - database session
            name: str - automaton string
            include_blob: bool - set to true to include the binary data. False otherwise

        Returns:
            Dictionary representation of the AutomatonTable
    """
    row = db.query(AutomatonTable).filter(AutomatonTable.name == name).one_or_none()
    if row is None:
        return None
    
    return {
        "id": row.id,
        "name": row.name,
        "width": row.width,
        "height": row.height,
        "frames": row.frames,
        "modified_at": row.modified_at,
        "cells": deserialize_cells(row.data) if include_blob else None
    }

def get_arguments_for_automaton(db: Session, automaton_id: int):
    """
        Helper query
    """
    stmt = (
        select(CellArguments)
        .join(AutomatonCellArgs, CellArguments.id == AutomatonCellArgs.arg_id)
        .join(AutomatonTable, AutomatonTable.id == AutomatonCellArgs.automaton_id)
        .where(AutomatonTable.id == automaton_id)
    )
    return db.execute(stmt).scalars().all()

def get_automaton(db: Session, name: str) -> AutomatonDto:
    """
    Get automaton dto. Returns a data in the format that allows for an easy creation of the automaton.

    Arguments:
        db: Session - database session
        name: str - name of the automaton

    Returns:
        AutomatonDto: dataclass - returns serialized automaton data.
    """
    dictionary = get_entry(db, name, True)
    if dictionary is None:
        raise RuntimeError(f"No automaton with name \"{name}\" found")

    args = list(map(lambda x: x.to_dict(), get_arguments_for_automaton(db, dictionary["id"])))
    mapping: Dict[int, Dict] = {}
    for a in args:
        id = a.pop("id")
        mapping[id] = a 

    positions: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    cells: Dict[Tuple[int, int], Cell] = {}

    for cell in dictionary["cells"]:
        c, nei = decode_cell(cell, mapping)
        position = (c.pos_x, c.pos_y)
        positions[position] = nei
        cells[position] = c

    for pos, cell in cells.items():
        neis = positions[pos]
        for nei in neis:
            cell.add_neighbor(cells[nei])

    return AutomatonDto(
        cell_map = cells,
        shape = (dictionary['width'], dictionary['height']),
        frame = dictionary['frames']
    )

def delete_entry(db: Session, name: str) -> bool:
    """
    Deletes the entry from the automaton table and a joiner table.

    Arguments:
        db: Session - database session
        name: str - name of the automaton

    Returns:
        bool - status of the operation
    """
    row = db.query(AutomatonTable).filter(AutomatonTable.name == name).one_or_none()
    if row is None:
        return False
    
    automaton_id = row.id
    db.query(AutomatonCellArgs).filter(AutomatonCellArgs.automaton_id == automaton_id).delete()

    db.delete(row)
    db.commit()
    return True

def list_entries(db: Session) -> List[Dict]:
    """
    Returns the entries from the database in the dictionary format and without the binary data.

    Arguments:
        db: Session - database session
    
    Returns:
        List[Dict] - list of automatons in the dictionary format and without the binary data (see get_entry for the details)
    """
    entries = db.query(AutomatonTable).all()
    if entries is None:
        return None
    res = []
    for entry in entries:
        res.append(get_entry(db, entry.name, False))
    return res