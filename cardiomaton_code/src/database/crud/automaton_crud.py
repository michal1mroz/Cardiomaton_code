from typing import Optional, Dict, Any, Callable, List
from sqlalchemy.orm import Session
from datetime import datetime

from src.database.models.automaton import AutomatonTable
from src.database.utils.cell_utils import serialize_cells, deserialize_cells

from src.models.cell import Cell

def create_or_overwrite_entry(
        db: Session,
        name: str,
        cells: List[Cell],
        width: int,
        height: int,
        frames: int,
) -> AutomatonTable:
    blob = serialize_cells(cells)
    existing = db.query(AutomatonTable).filter(AutomatonTable.name == name).one_or_none()

    if existing is not None:
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
    db.commit()
    db.refresh(row)
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

def delete_entry(db: Session, name: str) -> bool:
    row = db.query(AutomatonTable).filter(AutomatonTable.name == name).one_or_none()
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True