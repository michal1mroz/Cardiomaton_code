from typing import Optional, Dict, Any, Callable, List, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from src.models.automaton import Automaton
from src.database.models.automaton_cell_args import AutomatonCellArgs
from src.database.models.cell_arguments import CellArguments
from src.database.models.automaton import AutomatonTable
from src.database.utils.cell_utils import serialize_cells, deserialize_cells, decode_cell

from src.models.cell import Cell

def get_or_create_cell_arguments(db: Session,
                                 cell_data_dict: Dict[str, Any]) -> int:
    stmt = select(CellArguments).filter_by(**cell_data_dict)
    row = db.execute(stmt).scalars().first()
    if row:
        return row.id
    
    new_row = CellArguments(**cell_data_dict)
    db.add(new_row)
    db.flush()
    return new_row.id

def create_or_overwrite_entry(
        db: Session,
        name: str,
        cells: List[Cell],
        width: int,
        height: int,
        frames: int,
) -> AutomatonTable:
    mapping: Dict[frozenset, int] = {}
    for cell in cells:
        frozen = frozenset(cell.cell_data.items())
        if frozen not in mapping:
            arg_id = get_or_create_cell_arguments(db, cell.cell_data)
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
    stmt = (
        select(CellArguments)
        .join(AutomatonCellArgs, CellArguments.id == AutomatonCellArgs.arg_id)
        .join(AutomatonTable, AutomatonTable.id == AutomatonCellArgs.automaton_id)
        .where(AutomatonTable.id == automaton_id)
    )
    return db.execute(stmt).scalars().all()

def get_automaton(db: Session, name: str) -> Automaton:
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
        position = c.position
        positions[position] = nei
        cells[position] = c

    for pos, cell in cells.items():
        neis = positions[pos]
        for nei in neis:
            cell.add_neighbour(cells[nei])
    
    return Automaton(shape=(dictionary["width"], dictionary["height"]), cells=cells, frame=dictionary["frames"]) 

def delete_entry(db: Session, name: str) -> bool:
    row = db.query(AutomatonTable).filter(AutomatonTable.name == name).one_or_none()
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True